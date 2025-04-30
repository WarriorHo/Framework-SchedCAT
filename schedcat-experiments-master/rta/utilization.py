import copy
import random
from functools import partial
from toolbox.stats import mean
from schedcat.model.tasks import SporadicTask, TaskSystem
import schedcat.generator.generator_emstada as emstada
from toolbox.io import write_data, Config
# from exp.overhead import *
# from exp.analysis import *
# from exp.urcu import *
# from exp.parsec import *
from rta import bound_response_times
from rta_omnilog import bound_response_times_omnilog
from rta_nodrop import bound_response_times_nodrop
from datetime import datetime
import os
import socket
import sys
import time

PERIODS = { 
    '10-100': (10, 100),
}

def assign_fp_preemption_levels(all_tasks):
    # prioritized in index order
    for i, t in enumerate(all_tasks):
        t.preemption_level = i

def generate_task_set(conf):
    ts = TaskSystem()
    for cpuid in range(0, int(conf.num_cpus)):
        ntask = int(conf.num_task)
        u = float(conf.util)
        # 1
        tmp = emstada.gen_taskset(PERIODS[conf.periods], 'unif', ntask, u, 0.01)
        for t in tmp:
            t.partition = cpuid
            t.syscall_count = 200
        ts.extend(tmp)
    ts.sort_by_period()
    ts.assign_ids()
    assign_fp_preemption_levels(ts)
    return ts

def generate_nodrop_task_set(conf, standard_taskset):
    taskset = copy.deepcopy(standard_taskset)
    min_period = min(t.period for t in taskset)
    q_k = min_period * conf.consumer_period_factor
    consumer = SporadicTask(0, q_k, q_k)
    consumer.syscall_count = conf.consumer_syscall_count
    consumer.is_consumer = True
    taskset.append(consumer)
    taskset.sort_by_period()
    return taskset

# RTA test functions
# def rta_test(taskset, oh, conf):
#     return (int(bound_response_times(conf.num_cpus, taskset)), 0)

def rta_test(taskset, oh, conf):
    sched = int(bound_response_times(conf.num_cpus, taskset))
    return (sched, 0)

# def rta_omnilog_test(taskset, oh, conf):
#     return (int(bound_response_times_omnilog(conf.num_cpus, taskset, conf.delta)), 0)

def rta_omnilog_test(taskset, oh, conf):
    sched = int(bound_response_times_omnilog(conf.num_cpus, taskset, conf.delta))
    return (sched, 0)

# def rta_nodrop_test(taskset, oh, conf):
#     nodrop_taskset = generate_nodrop_task_set(conf, taskset)
#     return (int(bound_response_times_nodrop(nodrop_taskset, conf.delta, conf.alpha, conf.beta)), 0)

def rta_nodrop_test(taskset, oh, conf):
    nodrop_taskset = generate_nodrop_task_set(conf, taskset)
    sched = int(bound_response_times_nodrop(nodrop_taskset, conf.delta, conf.alpha, conf.beta))
    return (sched, 0)

# Test setup
def setup_tests():
    return [
        ("#rta", rta_test),
        ("#rta_omnilog", rta_omnilog_test),
        ("#rta_nodrop", rta_nodrop_test),
    ]

# Core test runner
# def run_tests(confs, tests, oh):
#     for conf in confs:
#         samples = [[] for _ in tests]
#         for sample in range(int(conf.samples)):
#             if sample % 100 == 0:
#                 print("Finished {} samples for utilization {:.2f}".format(sample, conf.var))
#             ts = generate_task_set(conf)
#             for i, test in enumerate(tests):
#                 (sched, _) = test[1](ts, oh, conf)
#                 samples[i].append(sched)
#         row = [conf.var] + [mean(sample) for sample in samples]
#         yield row

def run_tests(confs, tests, oh):
    for conf in confs:
        samples = [[] for _ in tests]
        for sample in range(int(conf.samples)):
            # if sample % 100 == 0:
            #     print("Finished {} samples for utilization {:.2f}".format(sample, conf.var))
            ts = conf.make_taskset()
            for i, test in enumerate(tests):
                result = test[1](ts, oh, conf)
                sched = result[0]
                samples[i].append(sched)
        row = [conf.var] + [mean(sample) for sample in samples]
        yield row

# Utilization experiment
# def run_util_num_config(conf):
#     oh = None  # No overheads for these tests
#     util_range = [float(conf.util_num_min) + i * float(conf.step) 
#                   for i in range(int((float(conf.util_num_max) - float(conf.util_num_min)) / float(conf.step)) + 1)]
#     confs = [copy.copy(conf) for _ in util_range]
#     for i, util in enumerate(util_range):
#         confs[i].util = util
#         confs[i].var = util
#         confs[i].make_taskset = partial(generate_task_set, confs[i])

#     (titles, tests) = zip(*setup_tests())
#     header = ['UTILIZATION'] + list(titles)

#     data = run_tests(confs, tests, oh)
#     write_util_data(conf.output, data, header, conf)

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

# Output function (inspired by rta_comparison.py)
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
            self.delta = 0.1
            self.alpha = 0.2
            self.beta = 0.05
            self.consumer_period_factor = 1.0
            self.consumer_syscall_count = 200

    conf = Conf()
    EXPERIMENTS[conf.experiment](conf)