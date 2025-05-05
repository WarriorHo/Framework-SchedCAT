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

PERIODS = { 
    '10-100': (10, 100),
}

def assign_fp_preemption_levels(all_tasks):
    for i, t in enumerate(all_tasks):
        t.preemption_level = i

def generate_task_set(conf, syscall_count):
    ts = TaskSystem()
    for cpuid in range(int(conf.num_cpus)):
        ntask = int(conf.num_task)
        u = float(conf.util)
        user_tasks = emstada.gen_taskset(PERIODS[conf.periods], 'unif', ntask, u, 0.01)
        for user_task in user_tasks:
            user_task.partition = cpuid
            user_task.syscall_count = syscall_count
            user_task.is_consumer = False
            ts.append(user_task)
            
            consumer = SporadicTask(0, conf.consumer_period_factor * user_task.period, conf.consumer_period_factor * user_task.period)
            consumer.syscall_count = conf.consumer_syscall_count
            consumer.is_consumer = True
            consumer.partition = cpuid
            ts.append(consumer)
    
    ts.sort_by_period()
    ts.assign_ids()
    assign_fp_preemption_levels(ts)

    for user_task in [t for t in ts if not t.is_consumer]:
        consumer = next(c for c in ts if c.is_consumer and c.partition == user_task.partition)
        higher_prio_users = [t for t in ts if t.partition == user_task.partition and 
                             t.preemption_level < user_task.preemption_level and not t.is_consumer]
        if higher_prio_users:
            min_higher_prio = min(higher_prio_users, key=lambda t: t.preemption_level).preemption_level
            consumer.preemption_level = (min_higher_prio + user_task.preemption_level) / 2
        else:
            consumer.preemption_level = user_task.preemption_level - 0.5
    
    return ts

def rta_test(taskset, oh, conf, include_consumers=False):
    ts = taskset
    if not include_consumers:
        ts = TaskSystem([t for t in ts if not t.is_consumer])
    framework = get_framework('rta')
    for t in ts:
        t.cost = framework.calculate_execution_time(t)
    sched = int(bound_response_times(conf.num_cpus, ts))
    return (sched, 0)

def rta_omnilog_test(taskset, oh, conf, include_consumers=False):
    ts = taskset
    if not include_consumers:
        ts = TaskSystem([t for t in ts if not t.is_consumer])
    framework = get_framework('omnilog')
    for t in ts:
        t.cost = framework.calculate_execution_time(t)
    sched = int(bound_response_times_omnilog(conf.num_cpus, ts, framework.delta))
    return (sched, 0)

def rta_nodrop_test(taskset, oh, conf, include_consumers=True):
    ts = taskset
    if not include_consumers:
        ts = TaskSystem([t for t in ts if not t.is_consumer])
    framework = get_framework('nodrop')
    for t in ts:
        t.cost = framework.calculate_execution_time(t)
    sched = int(bound_response_times_nodrop(ts, framework.delta, framework.alpha, framework.beta))
    return (sched, 0)

def setup_tests():
    return [
        ("#rta", partial(rta_test, include_consumers=False)),
        ("#rta_omnilog", partial(rta_omnilog_test, include_consumers=False)),
        ("#rta_nodrop", partial(rta_nodrop_test, include_consumers=True)),
    ]

def run_tests(confs, tests, oh):
    for conf, syscall_count in confs:
        samples = [[] for _ in tests]
        for sample in range(int(conf.samples)):
            if sample % 50 == 0:
                print("Finished {} samples for syscall_count {}".format(sample, syscall_count))
            ts = generate_task_set(conf, syscall_count)
            for i, test in enumerate(tests):
                result = test[1](ts, oh, conf)
                sched = result[0]
                samples[i].append(sched)
        row = [syscall_count] + [mean(sample) for sample in samples]
        yield row

def run_syscall_count_config(conf):
    start_time = time.time()
    oh = None
    syscall_count_range = range(conf.syscall_count_min, conf.syscall_count_max + 1, conf.syscall_count_step)
    confs = [(copy.copy(conf), syscall_count) for syscall_count in syscall_count_range]

    tests = setup_tests()
    header = ['SYSCALL_COUNT'] + [title for title, _ in tests]
    data = run_tests(confs, tests, oh)
    completed_time = time.time()
    write_util_data(conf.output, data, header, conf, start_time, completed_time)

def write_util_data(output_file, data, header, conf, start_time, completed_time):
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(output_file, 'w') as f:
        f.write("############### CONFIGURATION ###############\n")
        for key, value in conf.__dict__.items():
            f.write("# {:<15}: {}\n".format(key, value))
        f.write("################ ENVIRONMENT ################\n")
        f.write("# CWD............: {}\n".format(os.getcwd()))
        f.write("# Host...........: {}\n".format(socket.gethostname()))
        f.write("# Python.........: {}\n".format(sys.version.split()[0]))
        f.write("#################### DATA ###################\n")
        f.write("# " + " ".join(["{0:>13}".format(h) for h in header]) + "\n")
        for row in data:
            f.write(" ".join(["{0:>13}".format(str(x)) for x in row]) + "\n")
        f.write("#################### RUN ####################\n")
        f.write("# Started........: {}\n".format(datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')))
        f.write("# Completed......: {}\n".format(datetime.fromtimestamp(completed_time).strftime('%Y-%m-%d %H:%M:%S')))
        f.write("# Duration.......: {:.2f} seconds\n".format(completed_time - start_time))

EXPERIMENTS = {
    'syscall_count': run_syscall_count_config,
}

if __name__ == "__main__":
    class Conf:
        def __init__(self):
            self.experiment = 'syscall_count'
            self.output = 'output/syscall_sched.txt'
            self.num_task = 10
            self.samples = 5000
            self.periods = '10-100'
            self.num_cpus = 1
            self.util = 0.8
            self.syscall_count_min = 0
            self.syscall_count_max = 1000
            self.syscall_count_step = 50
            self.consumer_period_factor = 1.0
            self.consumer_syscall_count = 200

    conf = Conf()
    EXPERIMENTS[conf.experiment](conf)