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

PERIODS = { 
    '10-100': (10, 100),
}

def assign_fp_preemption_levels(all_tasks):
    # Prioritized in index order
    for i, t in enumerate(all_tasks):
        t.preemption_level = i

def generate_task_set(conf, syscall_count=None):
    ts = TaskSystem()
    for cpuid in range(0, int(conf.num_cpus)):
        ntask = int(conf.num_task)
        u = float(conf.util)
        tmp = emstada.gen_taskset(PERIODS[conf.periods], 'unif', ntask, u, 0.01)
        for t in tmp:
            t.partition = cpuid
            # Use provided syscall_count if given, else default to 200
            t.syscall_count = syscall_count if syscall_count is not None else 200
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
def rta_test(taskset, oh, conf):
    sched = int(bound_response_times(conf.num_cpus, taskset))
    return (sched, 0)

def rta_omnilog_test(taskset, oh, conf):
    sched = int(bound_response_times_omnilog(conf.num_cpus, taskset, conf.delta))
    return (sched, 0)

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
def run_tests(confs, tests, oh):
    for conf in confs:
        samples = [[] for _ in tests]
        for sample in range(int(conf.samples)):
            ts = conf.make_taskset()
            for i, test in enumerate(tests):
                result = test[1](ts, oh, conf)
                sched = result[0]
                samples[i].append(sched)
        row = [conf.var] + [mean(sample) for sample in samples]
        yield row

# Utilization experiment
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

# System call count experiment
def run_syscall_num_config(conf):
    start_time = time.time()
    oh = None
    syscall_range = [int(conf.syscall_num_min) + i * int(conf.syscall_step) 
                     for i in range(int((int(conf.syscall_num_max) - int(conf.syscall_num_min)) / int(conf.syscall_step)) + 1)]
    confs = [copy.copy(conf) for _ in syscall_range]
    for i, syscall_count in enumerate(syscall_range):
        confs[i].syscall_count = syscall_count
        confs[i].var = syscall_count
        confs[i].make_taskset = partial(generate_task_set, confs[i], syscall_count)
    
    tests = setup_tests()
    header = ['SYSCALL_COUNT'] + [title for title, _ in tests]
    data = run_tests(confs, tests, oh)
    completed_time = time.time()
    write_util_data(conf.output, data, header, conf, start_time, completed_time)

# Output function
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
    'syscall_num': run_syscall_num_config,
}

CONFIG_GENERATORS = {
    'rtas18': lambda options: None,
}

if __name__ == "__main__":
    class Conf:
        def __init__(self):
            self.experiment = 'syscall_num'  # Set to run the new experiment
            self.output = 'output/syscall_schedulability_comparison.txt'
            self.num_task = 10
            self.samples = 5000
            self.periods = '10-100'
            self.num_cpus = 1
            self.util = 0.9  # Fixed utilization for syscall experiment
            self.util_num_min = 0.1  # Kept for util_num experiment
            self.util_num_max = 1.0  # Kept for util_num experiment
            self.step = 0.01  # Kept for util_num experiment
            self.delta = 0.1
            self.alpha = 0.2
            self.beta = 0.05
            self.consumer_period_factor = 1.0
            self.consumer_syscall_count = 200
            # New parameters for syscall experiment
            self.syscall_num_min = 0
            self.syscall_num_max = 1000
            self.syscall_step = 100

    conf = Conf()
    EXPERIMENTS[conf.experiment](conf)