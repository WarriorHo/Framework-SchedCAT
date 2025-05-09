import copy
import random
from functools import partial
from toolbox.stats import mean
from schedcat.model.tasks import SporadicTask, TaskSystem
import schedcat.generator.generator_emstada as emstada
from toolbox.io import write_data, Config
from rta import bound_response_times
from rta_omnilog import bound_response_times_omnilog
from rta_nodrop import bound_response_times_nodrop
from datetime import datetime
import os
import socket
import sys
import time
from params import AuditFramework, FRAMEWORKS, get_framework
from math import ceil
import contextlib

# Toggle between small dataset debug tests and full generated tests
SMALL_DATASET_TEST = False

# Helper for printing/writing task sets

def print_task_set(ts):
    """Print detailed information of the task set."""
    print("Task Set Details:")
    print("{:<5} {:<10} {:<5} {:<10} {:<20}".format('ID', 'Type', 'CPU', 'Period', 'Preemption Level'))
    print("-" * 60)
    for task in ts:
        task_type = "Consumer" if getattr(task, 'is_consumer', False) else "User"
        preemption_level = getattr(task, 'preemption_level', '')
        print("{:<5} {:<10} {:<5} {:<10} {:<20}".format(
            task.id,
            task_type,
            task.partition,
            task.period,
            preemption_level
        ))
    print("\n")

# Original utility functions and test setup

PERIODS = { 
    '10-100': (10, 100),
}


def generate_task_set(conf):
    ts = TaskSystem()
    for cpuid in range(int(conf.num_cpus)):
        ntask = int(conf.num_task)
        u = float(conf.util)
        user_tasks = emstada.gen_taskset(PERIODS[conf.periods], 'unif', ntask, u, 0.01)
        for user_task in user_tasks:
            user_task.partition = cpuid
            user_task.syscall_count = 200
            user_task.is_consumer = False
            ts.append(user_task)
    user_ts = TaskSystem([t for t in ts if not t.is_consumer])
    user_ts.sort_by_period()
    for i, t in enumerate(user_ts):
        t.preemption_level = float(i)
    for user_task in user_ts:
        consumer = SporadicTask(0,
            conf.consumer_period_factor * user_task.period,
            conf.consumer_period_factor * user_task.period)
        consumer.syscall_count = conf.consumer_syscall_count
        consumer.is_consumer = True
        consumer.partition = user_task.partition
        consumer.preemption_level = user_task.preemption_level - 0.5
        ts.append(consumer)
    ts.sort(key=lambda t: t.preemption_level)
    ts.assign_ids()
    return ts


def iter_partitions_ts(taskset):
    partitions = {}
    for t in taskset:
        partitions.setdefault(t.partition, []).append(t)
    for p in partitions.values():
        yield TaskSystem(p)


def rta_test(taskset, oh, conf, include_consumers=False):
    ts = TaskSystem(taskset)
    if not include_consumers:
        ts = TaskSystem([t for t in ts if not t.is_consumer])
    framework = get_framework('rta')
    for t in ts:
        t.cost = framework.calculate_execution_time(t)
    for partition in iter_partitions_ts(ts):
        if not bound_response_times(1, partition):
            return (0, 0)
    return (1, 0)


def rta_omnilog_test(taskset, oh, conf, include_consumers=False):
    ts = TaskSystem(taskset)
    if not include_consumers:
        ts = TaskSystem([t for t in ts if not t.is_consumer])
    framework = get_framework('omnilog')
    for partition in iter_partitions_ts(ts):
        part_ts = TaskSystem(partition)
        if not part_ts:
            continue
        min_period_task = min(part_ts, key=lambda t: t.period)
        q_sigma = min_period_task.period
        # single consumer
        consumer = SporadicTask(0, q_sigma, q_sigma)
        consumer.syscall_count = 0
        consumer.is_consumer = True
        consumer.preemption_level = -1
        consumer.partition = part_ts[0].partition
        part_ts.append(consumer)
        for t in part_ts:
            t.cost = framework.calculate_execution_time(t)
        if not bound_response_times_omnilog(1, part_ts, framework.delta, framework.beta):
            return (0, 0)
    return (1, 0)


def rta_nodrop_test(taskset, oh, conf, include_consumers=True):
    ts = TaskSystem(taskset)
    if not include_consumers:
        ts = TaskSystem([t for t in ts if not t.is_consumer])
    framework = get_framework('nodrop')
    for partition in iter_partitions_ts(ts):
        part_ts = TaskSystem(partition)
        for t in part_ts:
            t.cost = framework.calculate_execution_time(t)
        if not bound_response_times_nodrop(part_ts, framework.delta, framework.alpha, framework.beta):
            return (0, 0)
    return (1, 0)


def setup_tests():
    return [
        ("#rta", partial(rta_test, include_consumers=False)),
        ("#rta_omnilog", partial(rta_omnilog_test, include_consumers=False)),
        ("#rta_nodrop", partial(rta_nodrop_test, include_consumers=True)),
    ]


def run_tests(confs, tests, oh):
    for conf in confs:
        samples = [[] for _ in tests]
        for sample in range(int(conf.samples)):
            if sample % 100 == 0:
                print("Finished {} samples for utilization {:.2f}".format(sample, conf.var))
            ts = conf.make_taskset()
            for i, test in enumerate(tests):
                result = test[1](ts, oh, conf)
                samples[i].append(result[0])
        yield [conf.var] + [mean(s) for s in samples]


def run_util_num_config(conf):
    start_time = time.time()
    oh = None
    util_range = [float(conf.util_num_min) + i * float(conf.step)
                  for i in range(int((float(conf.util_num_max) - float(conf.util_num_min)) / float(conf.step)) + 1)]
    confs = [copy.copy(conf) for _ in util_range]
    for i, util in enumerate(util_range):
        confs[i].util = util
        confs[i].var = util
        confs[i].make_taskset = partial(generate_task_set, confs[i])
    tests = setup_tests()
    header = ['UTILIZATION'] + [t for t, _ in tests]
    data = run_tests(confs, tests, oh)
    completed_time = time.time()
    write_util_data(conf.output, data, header, conf, start_time, completed_time)


def write_util_data(output_file, data, header, conf, start_time, completed_time):
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(output_file, 'w') as f:
        f.write("############### CONFIGURATION ###############\n")
        for key, value in conf.__dict__.items():
            f.write("# {:<15}: {}\n".format(key, value))
        f.write("#################### DATA ###################\n")
        f.write("# " + " ".join("{:>13}".format(h) for h in header) + "\n")
        for row in data:
            f.write(" ".join("{:>13}".format(str(x)) for x in row) + "\n")


if __name__ == "__main__":
    class Conf:
        def __init__(self):
            self.experiment = 'util_num'
            self.output = 'output/test_util_sched.txt'
            self.num_task = 10
            self.samples = 5000
            self.periods = '10-100'
            self.num_cpus = 1
            self.util_num_min = 0.1
            self.util_num_max = 1.0
            self.step = 0.01
            self.consumer_period_factor = 1.0
            self.consumer_syscall_count = 200
            self.util = 0.1

    conf = Conf()

    if SMALL_DATASET_TEST:
        # Define small sets
        small_sets = [
            [(2.3, 10, 1, 0), (3.6, 15, 2, 1)],
            [(1.5, 10, 1, 0), (2.5, 15, 2, 1)],
            [(3.0, 12, 1, 0), (4.0, 18, 3, 1)],
        ]
        # Prepare output
        out_file = 'output/small_taskset_test_results.txt'
        out_dir = os.path.dirname(out_file)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir)
        with open(out_file, 'w') as fout:
            for i, params in enumerate(small_sets, 1):
                header = "=== Small Task Set #{} ===".format(i)
                print(header)
                fout.write(header + "\n")
                ts_omni = TaskSystem()
                ts_nodrop = TaskSystem()
                # build base user tasks
                for cost, period, scount, plevel in params:
                    t = SporadicTask(cost, period)
                    t.syscall_count = scount
                    t.preemption_level = plevel
                    t.is_consumer = False
                    t.partition = 0
                    ts_omni.append(t)
                    ts_nodrop.append(t)
                # single consumer for omnilog
                min_p = min(t.period for t in ts_omni)
                c_o = SporadicTask(0, min_p)
                c_o.syscall_count = 0
                c_o.preemption_level = -1
                c_o.is_consumer = True
                c_o.partition = 0
                ts_omni.append(c_o)
                ts_omni.assign_ids()
                # per-task consumers for nodrop
                user_tasks = list(ts_nodrop)
                for ut in user_tasks:
                    c_n = SporadicTask(0, conf.consumer_period_factor * ut.period)
                    c_n.syscall_count = conf.consumer_syscall_count
                    c_n.is_consumer = True
                    c_n.partition = ut.partition
                    c_n.preemption_level = ut.preemption_level - 0.5
                    ts_nodrop.append(c_n)
                ts_nodrop.assign_ids()
                # log task sets
                print_task_set(ts_omni)
                print_task_set(ts_nodrop)
                # run analyses
                f_o = get_framework('omnilog')
                sched_o = bound_response_times_omnilog(1, ts_omni, f_o.delta, f_o.beta)
                line_o = "Omnilog schedulable: {}".format(bool(sched_o))
                print(line_o)
                fout.write(line_o + "\n")
                f_n = get_framework('nodrop')
                sched_n = bound_response_times_nodrop(ts_nodrop, f_n.delta, f_n.alpha, f_n.beta)
                line_n = "Nodrop schedulable: {}".format(bool(sched_n))
                print(line_n)
                fout.write(line_n + "\n\n")
    else:
        # Full generated tests
        ts = generate_task_set(conf)
        ts.assign_ids()
        print_task_set(ts)
        for title, test_fn in setup_tests():
            res = test_fn(ts, None, conf)
            print("Test {} result: {}".format(title, res))

    # optionally: EXPERIMENTS[conf.experiment](conf)