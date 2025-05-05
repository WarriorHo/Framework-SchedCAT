# V1.0 #
# -*- coding: utf-8 -*-
# import random
# import time
# import os
# import sys
# import socket
# from schedcat.model.tasks import TaskSystem, SporadicTask
# from rta_nodrop import is_schedulable_with_nodrop
# from datetime import datetime

# class Task(SporadicTask):
#     def __init__(self, execution_time, period, deadline):
#         super(Task, self).__init__(execution_time, period, deadline)
#         self.jitter = 0
#         self.suspended = 0
#         self.prio_inversion = 0
#         self.cost = execution_time
#         self.syscall_count = random.randint(0, 10)
#         # Randomly mark 20% tasks as consumers
#         self.is_consumer = random.random() < 0.2

# conf = {
#     'experiment': 'rta_nodrop_schedulability',
#     'output_file': 'output/rta_nodrop_schedulability.txt',
#     'num_tasks': 10,           # Number of tasks per task set
#     'samples': 5000,           # Number of task sets per utilization level
#     'period_min': 10,          # Minimum task period
#     'period_max': 100,         # Maximum task period
#     'num_cpus': 1,             # Number of processors
#     'util_min': 0.1,           # Minimum utilization
#     'util_max': 1.0,           # Maximum utilization
#     'util_step': 0.05,         # Utilization step size
#     'delta': 0.1,              # System call overhead
#     'alpha': 2.0,              # Constant audit overhead
#     'beta': 0.5,               # Per-call audit processing
# }

# def uunifast(n, target_util):
#     utilizations = []
#     sum_u = target_util
#     for i in range(n - 1):
#         next_sum_u = sum_u * (1 - random.random() ** (1.0 / (n - i)))
#         utilizations.append(sum_u - next_sum_u)
#         sum_u = next_sum_u
#     utilizations.append(sum_u)
#     return utilizations

# def generate_task_set(conf, target_util):
#     taskset = TaskSystem()
#     utilizations = uunifast(conf['num_tasks'], target_util)
    
#     for u in utilizations:
#         period = random.randint(conf['period_min'], conf['period_max'])
#         cost = max(1, int(u * period))
#         task = Task(cost, period, period)
#         taskset.append(task)
    
#     taskset.sort(key=lambda t: t.period)  # Sort by period
#     return taskset

# def run_rta_test(taskset, num_cpus, delta, alpha, beta):
#     return 1 if is_schedulable_with_nodrop(taskset, num_cpus, delta, alpha, beta) else 0

# def write_output_file(output_file, conf, data, start_time, end_time):
#     output_dir = os.path.dirname(output_file)
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)
#     with open(output_file, 'w') as f:
#         f.write("############### CONFIGURATION ###############\n")
#         for key, value in conf.items():
#             f.write("# {0:<15}: {1}\n".format(key, value))

#         f.write("################ ENVIRONMENT ################\n")
#         f.write("# CWD............: {0}\n".format(os.getcwd()))
#         f.write("# Host...........: {0}\n".format(socket.gethostname()))
#         f.write("# Python.........: {0}\n".format(sys.version.split()[0]))

#         f.write("#################### DATA ###################\n")
#         f.write("#  UTILIZATION  # Schedulability\n")
#         for util, sched_ratio in data:
#             f.write("{0:>14.2f} {1:>14.2f}\n".format(util, sched_ratio))

#         f.write("#################### RUN ####################\n")
#         f.write("# Started........: {0}\n".format(datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')))
#         f.write("# Completed......: {0}\n".format(datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')))
#         f.write("# Duration.......: {0:.2f} seconds\n".format(end_time - start_time))

# def run_experiment(conf):
#     start_time = time.time()
#     data = []
#     util_range = [conf['util_min'] + i * conf['util_step'] 
#                   for i in range(int((conf['util_max'] - conf['util_min']) / conf['util_step']) + 1)]

#     for util in util_range:
#         sched_sum = 0
#         for _ in range(conf['samples']):
#             taskset = generate_task_set(conf, util)
#             sched_sum += run_rta_test(taskset, conf['num_cpus'], conf['delta'], conf['alpha'], conf['beta'])
#         sched_ratio = sched_sum / float(conf['samples'])
#         data.append((util, sched_ratio))

#     end_time = time.time()
#     write_output_file(conf['output_file'], conf, data, start_time, end_time)

# if __name__ == "__main__":
#     run_experiment(conf)

# V2.0 #
import random
import time
import os
import sys
import socket
from schedcat.model.tasks import TaskSystem, SporadicTask
from rta_nodrop import bound_response_times_nodrop
from datetime import datetime

class Task(SporadicTask):
    def __init__(self, execution_time, period, deadline):
        super(Task, self).__init__(execution_time, period, deadline)
        self.jitter = 0
        self.suspended = 0
        self.prio_inversion = 0
        self.cost = execution_time
        self.syscall_count = random.randint(0, 10)

conf = {
    'experiment': 'rta_nodrop_schedulability',
    'output_file': 'output/rta_nodrop_schedulability.txt',
    'num_tasks': 10,
    'samples': 5000,
    'period_min': 10,
    'period_max': 100,
    'num_cpus': 1,
    'util_min': 0.1,
    'util_max': 1.0,
    'util_step': 0.05,
    'delta': 0.1,              # Overhead per system call for regular tasks
    'alpha': 0.2,              # Constant overhead per consumer invocation
    'beta': 0.05,              # Processing overhead per system call in consumer
    'consumer_period_factor': 1024.0,  # Factor to scale consumer period
    'consumer_syscall_count': 20,   # Number of system calls processed by consumer
}

def uunifast(n, target_util):
    utilizations = []
    sum_u = target_util
    for i in range(n - 1):
        next_sum_u = sum_u * (1 - random.random() ** (1.0 / (n - i)))
        utilizations.append(sum_u - next_sum_u)
        sum_u = next_sum_u
    utilizations.append(sum_u)
    return utilizations

def generate_task_set(conf, target_util):
    taskset = TaskSystem()
    utilizations = uunifast(conf['num_tasks'], target_util)
    for u in utilizations:
        period = random.randint(conf['period_min'], conf['period_max'])
        cost = max(1, int(u * period))
        task = Task(cost, period, period)
        taskset.append(task)
    taskset.sort_by_period()
    return taskset

def create_consumers(regular_tasks, conf):
    min_period = min(t.period for t in regular_tasks)
    q_k = min_period * conf['consumer_period_factor']
    consumer = Task(0, q_k, q_k)  # cost=0, period=q_k, deadline=q_k
    consumer.syscall_count = conf['consumer_syscall_count']
    consumer.is_consumer = True
    return [consumer]

def run_rta_test(regular_tasks, conf):
    consumers = create_consumers(regular_tasks, conf)
    full_system = TaskSystem(regular_tasks + consumers)
    full_system.sort_by_period()
    return 1 if bound_response_times_nodrop(full_system, conf['delta'], conf['alpha'], conf['beta']) else 0

def write_output_file(output_file, conf, data, start_time, end_time):
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(output_file, 'w') as f:
        f.write("############### CONFIGURATION ###############\n")
        for key, value in conf.items():
            f.write("# {0:<15}: {1}\n".format(key, value))
        f.write("################ ENVIRONMENT ################\n")
        f.write("# CWD............: {0}\n".format(os.getcwd()))
        f.write("# Host...........: {0}\n".format(socket.gethostname()))
        f.write("# Python.........: {0}\n".format(sys.version.split()[0]))
        f.write("#################### DATA ###################\n")
        f.write("#  UTILIZATION  # Schedulability\n")
        for util, sched_ratio in data:
            f.write("{0:>14.2f} {1:>14.2f}\n".format(util, sched_ratio))
        f.write("#################### RUN ####################\n")
        f.write("# Started........: {0}\n".format(datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')))
        f.write("# Completed......: {0}\n".format(datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')))
        f.write("# Duration.......: {0:.2f} seconds\n".format(end_time - start_time))

def run_experiment(conf):
    start_time = time.time()
    data = []
    util_range = [conf['util_min'] + i * conf['util_step']
                  for i in range(int((conf['util_max'] - conf['util_min']) / conf['util_step']) + 1)]
    for util in util_range:
        sched_sum = 0
        for _ in range(conf['samples']):
            regular_tasks = generate_task_set(conf, util)
            sched_sum += run_rta_test(regular_tasks, conf)
        sched_ratio = sched_sum / float(conf['samples'])
        data.append((util, sched_ratio))
    end_time = time.time()
    write_output_file(conf['output_file'], conf, data, start_time, end_time)

if __name__ == "__main__":
    run_experiment(conf)