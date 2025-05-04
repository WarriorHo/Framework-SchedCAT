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

# def generate_task_set(conf):
#     ts = TaskSystem()
#     for cpuid in range(0, int(conf.num_cpus)):
#         ntask = int(conf.num_task)
#         u = float(conf.util)
#         # 1 don't need to randomly generate task, but i'm not sure
#         tmp = emstada.gen_taskset(PERIODS[conf.periods], 'unif', ntask, u, 0.01)
#         for t in tmp:
#             t.partition = cpuid
#             t.syscall_count = 200
#         ts.extend(tmp)
#     ts.sort_by_period()
#     ts.assign_ids()
#     assign_fp_preemption_levels(ts)
#     return ts

# def generate_nodrop_task_set(conf, standard_taskset):
#     taskset = copy.deepcopy(standard_taskset)
#     min_period = min(t.period for t in taskset)
#     q_k = min_period * conf.consumer_period_factor
#     consumer = SporadicTask(0, q_k, q_k)
#     consumer.syscall_count = conf.consumer_syscall_count
#     consumer.is_consumer = True
#     taskset.append(consumer)
#     taskset.sort_by_period()
#     return taskset

# def generate_task_set(conf):
#     ts = TaskSystem()
#     for cpuid in range(int(conf.num_cpus)):
#         ntask = int(conf.num_task)
#         u = float(conf.util)
#         user_tasks = emstada.gen_taskset(PERIODS[conf.periods], 'unif', ntask, u, 0.01)
#         for user_task in user_tasks:
#             user_task.partition = cpuid
#             user_task.syscall_count = 200
#             user_task.is_consumer = False
#             ts.append(user_task)
            
#             consumer = SporadicTask(0, conf.consumer_period_factor * user_task.period, conf.consumer_period_factor * user_task.period)
#             consumer.syscall_count = conf.consumer_syscall_count
#             consumer.is_consumer = True
#             consumer.partition = cpuid
#             consumer.preemption_level = user_task.preemption_level - 0.5
#             ts.append(consumer)
    
#     ts.sort_by_period()
#     ts.assign_ids()
#     assign_fp_preemption_levels(ts)
#     return ts

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

# def calculate_execution_time(task, framework, conf):
#     if framework == 'rta':
#         return task.cost
#     elif framework == 'omnilog':
#         return task.cost + task.syscall_count * conf.delta
#     elif framework == 'nodrop':
#         return task.cost + task.syscall_count * conf.delta
#     else:
#         raise ValueError(f"Unknown framework: {framework}")

# def calculate_consumer_execution_time(consumer, conf):
#     return conf.alpha + consumer.syscall_count * conf.beta

# def rta_test(taskset, oh, conf):
#     sched = int(bound_response_times(conf.num_cpus, taskset))
#     return (sched, 0)

def rta_test(taskset, oh, conf, include_consumers=False):
    ts = taskset
    if not include_consumers:
        ts = TaskSystem([t for t in ts if not t.is_consumer])
    # framework = AuditFramework('rta')
    framework = get_framework('rta')
    for t in ts:
        # t.cost = calculate_execution_time(t, 'rta', conf)
        t.cost = framework.calculate_execution_time(t)
    sched = int(bound_response_times(conf.num_cpus, ts))
    return (sched, 0)

# def rta_omnilog_test(taskset, oh, conf):
#     sched = int(bound_response_times_omnilog(conf.num_cpus, taskset, conf.delta))
#     return (sched, 0)

def rta_omnilog_test(taskset, oh, conf, include_consumers=False):
    ts = taskset
    if not include_consumers:
        ts = TaskSystem([t for t in ts if not t.is_consumer])
    # framework = AuditFramework('omnilog', delta=conf.delta)
    framework = get_framework('omnilog')
    for t in ts:
        # t.cost = calculate_execution_time(t, 'omnilog', conf)
        t.cost = framework.calculate_execution_time(t)
    sched = int(bound_response_times_omnilog(conf.num_cpus, ts, framework.delta))
    return (sched, 0)

# def rta_nodrop_test(taskset, oh, conf):
#     nodrop_taskset = generate_nodrop_task_set(conf, taskset)
#     sched = int(bound_response_times_nodrop(nodrop_taskset, conf.delta, conf.alpha, conf.beta))
#     return (sched, 0)

def rta_nodrop_test(taskset, oh, conf, include_consumers=True):
    ts = taskset
    if not include_consumers:
        ts = TaskSystem([t for t in ts if not t.is_consumer])
    # framework = AuditFramework('nodrop', delta=conf.delta, alpha=conf.alpha, beta=conf.beta)
    framework = get_framework('nodrop')
    for t in ts:
        # if t.is_consumer:
        #     t.cost = calculate_consumer_execution_time(t, conf)
        # else:
        #     t.cost = calculate_execution_time(t, 'nodrop', conf)
        t.cost = framework.calculate_execution_time(t)
    sched = int(bound_response_times_nodrop(ts, framework.delta, framework.alpha, framework.beta))
    return (sched, 0)

# Test setup
# def setup_tests():
#     return [
#         ("#rta", rta_test),
#         ("#rta_omnilog", rta_omnilog_test),
#         ("#rta_nodrop", rta_nodrop_test),
#     ]

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
                sched = result[0]
                samples[i].append(sched)
        row = [conf.var] + [mean(sample) for sample in samples]
        yield row

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
    header = ['UTILIZATION'] + [title for title, _ in tests]
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
    'util_num': run_util_num_config,
}

CONFIG_GENERATORS = {
    'rtas18': lambda options: None,
}

if __name__ == "__main__":
    class Conf:
        def __init__(self):
            self.experiment = 'util_num'
            self.output = 'output/utilization_schedulability_comparison.txt'
            self.num_task = 10
            self.samples = 5000
            self.periods = '10-100'
            self.num_cpus = 1
            self.util_num_min = 0.1
            self.util_num_max = 1.0
            self.step = 0.01
            # self.delta = 0.1
            # self.alpha = 0.2
            # self.beta = 0.05
            self.consumer_period_factor = 1.0
            self.consumer_syscall_count = 200

    conf = Conf()
    EXPERIMENTS[conf.experiment](conf)