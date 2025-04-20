# V1.0 #
# rta_schedulability have question, datas are strange #
# import random
# import time
# import os
# import sys
# import socket
# from schedcat.model.tasks import TaskSystem, SporadicTask
# from rta import bound_response_times

# class Task(SporadicTask):
#     def __init__(self, execution_time, period, deadline):
#         super(Task, self).__init__(execution_time, period, deadline)
#         self.jitter = 0
#         self.suspended = 0
#         self.prio_inversion = 0
#         self.cost = execution_time

# conf = {
#     'experiment': 'rta_schedulability',
#     'output_file': 'output/rta_schedulability.txt',
#     'num_tasks': 10,
#     'samples': 500,
#     'period_min': 10,
#     'period_max': 100,
#     'num_cpus': 1,
#     'util_min': 0.6,
#     'util_max': 0.92,
#     'util_step': 0.03,
# }

# def generate_task_set(conf, utilization):
#     taskset = TaskSystem()
#     total_util = utilization
#     for _ in range(conf['num_tasks']):
#         period = random.randint(conf['period_min'], conf['period_max'])

#         cost = int((total_util / conf['num_tasks']) * period)
#         if cost < 1:
#             cost = 1
#         task = Task(cost, period, period)
#         taskset.append(task)
        
#     taskset.sort_by_period()
#     return taskset

# def run_rta_test(taskset, num_cpus):
#     return int(bound_response_times(num_cpus, taskset))

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
#         f.write("# Started........: {0}\n".format(start_time))
#         f.write("# Completed......: {0}\n".format(end_time))
#         f.write("# Duration.......: {0:.2f} seconds\n".format(end_time - start_time))

# def run_experiment(conf):
#     start_time = time.time()
#     data = []
#     util_min = conf['util_min']
#     util_max = conf['util_max']
#     step = conf['util_step']
#     num_samples = conf['samples']

#     for util in [util_min + i * step for i in range(int((util_max - util_min) / step) + 1)]:
#         sched_sum = 0
#         for _ in range(num_samples):
#             taskset = generate_task_set(conf, util)
#             sched = run_rta_test(taskset, conf['num_cpus'])
#             sched_sum += sched
#         sched_ratio = sched_sum / num_samples
#         data.append((util, sched_ratio))

#     end_time = time.time()
#     write_output_file(conf['output_file'], conf, data, start_time, end_time)

# if __name__ == "__main__":
#     run_experiment(conf)

# V2.0 #
# due to the answer of schedualbility showed as 0 or 1, i need to change the code as V3.0
# import random
# import time
# import os
# import sys
# import socket
# from schedcat.model.tasks import TaskSystem, SporadicTask
# from rta import bound_response_times

# class Task(SporadicTask):
#     def __init__(self, execution_time, period, deadline):
#         super(Task, self).__init__(execution_time, period, deadline)
#         self.jitter = 0
#         self.suspended = 0
#         self.prio_inversion = 0
#         self.cost = execution_time

# conf = {
#     'experiment': 'rta_schedulability',
#     'output_file': 'output/rta_schedulability.txt',
#     'num_tasks': 10,
#     'samples': 500,
#     'period_min': 10,
#     'period_max': 100,
#     'num_cpus': 1,
#     'util_min': 0.6,
#     'util_max': 0.92,
#     'util_step': 0.01,
# }

# def generate_task_set(conf, utilization):
#     taskset = TaskSystem()
#     remaining_util = utilization
#     for i in range(conf['num_tasks']):
#         period = random.randint(conf['period_min'], conf['period_max'])

#         if i == conf['num_tasks'] - 1:
#             util_share = remaining_util
#         else:
#             util_share = random.uniform(0, remaining_util * 2 / (conf['num_tasks'] - i))
#             remaining_util -= util_share
#             if remaining_util < 0:
#                 remaining_util = 0
#                 util_share = 0
#         cost = int(util_share * period)
#         if cost < 1:
#             cost = 1
#         task = Task(cost, period, period)
#         taskset.append(task)
    
#     taskset.sort_by_period()
#     return taskset

# def run_rta_test(taskset, num_cpus):
#     return int(bound_response_times(num_cpus, taskset))

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
#         f.write("# Started........: {0}\n".format(start_time))
#         f.write("# Completed......: {0}\n".format(end_time))
#         f.write("# Duration.......: {0:.2f} seconds\n".format(end_time - start_time))

# def run_experiment(conf):
#     start_time = time.time()
#     data = []
#     util_min = conf['util_min']
#     util_max = conf['util_max']
#     step = conf['util_step']
#     num_samples = conf['samples']

#     for util in [util_min + i * step for i in range(int((util_max - util_min) / step) + 1)]:
#         sched_sum = 0
#         for _ in range(num_samples):
#             taskset = generate_task_set(conf, util)
#             sched = run_rta_test(taskset, conf['num_cpus'])
#             sched_sum += sched
#         sched_ratio = sched_sum / num_samples
#         data.append((util, sched_ratio))

#     end_time = time.time()
#     write_output_file(conf['output_file'], conf, data, start_time, end_time)

# if __name__ == "__main__":
#     run_experiment(conf)


# V3.0
# import random
# import time
# import os
# import sys
# import socket
# from schedcat.model.tasks import TaskSystem, SporadicTask
# from rta import bound_response_times

# class Task(SporadicTask):
#     def __init__(self, execution_time, period, deadline):
#         super(Task, self).__init__(execution_time, period, deadline)
#         self.jitter = 0
#         self.suspended = 0
#         self.prio_inversion = 0
#         self.cost = execution_time

# conf = {
#     'experiment': 'rta_schedulability',
#     'output_file': 'output/rta_schedulability.txt',
#     'num_tasks': 10,
#     'samples': 500,
#     'period_min': 10,
#     'period_max': 100,
#     'num_cpus': 1,
#     'util_min': 0.6,
#     'util_max': 0.92,
#     'util_step': 0.01,
# }

# def generate_task_set(conf, target_util):
#     taskset = TaskSystem()
#     util_sum = target_util
#     for i in range(conf['num_tasks'] - 1):
#         util_share = random.uniform(0, util_sum / (conf['num_tasks'] - i))
#         util_sum -= util_share
#         period = random.randint(conf['period_min'], conf['period_max'])
#         cost = int(util_share * period)
#         if cost < 1:
#             cost = 1
#         task = Task(cost, period, period)
#         taskset.append(task)
    
#     period = random.randint(conf['period_min'], conf['period_max'])
#     cost = int(util_sum * period)
#     if cost < 1:
#         cost = 1
#     task = Task(cost, period, period)
#     taskset.append(task)
    
#     taskset.sort_by_period()
#     return taskset

# def run_rta_test(taskset, num_cpus):
#     return int(bound_response_times(num_cpus, taskset))

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
#         f.write("# Started........: {0}\n".format(start_time))
#         f.write("# Completed......: {0}\n".format(end_time))
#         f.write("# Duration.......: {0:.2f} seconds\n".format(end_time - start_time))

# def run_experiment(conf):
#     start_time = time.time()
#     data = []
#     util_min = conf['util_min']
#     util_max = conf['util_max']
#     step = conf['util_step']
#     num_samples = conf['samples']

#     for util in [util_min + i * step for i in range(int((util_max - util_min) / step) + 1)]:
#         sched_sum = 0
#         for _ in range(num_samples):
#             taskset = generate_task_set(conf, util)
#             sched = run_rta_test(taskset, conf['num_cpus'])
#             sched_sum += sched
#         sched_ratio = sched_sum / num_samples
#         data.append((util, sched_ratio))

#     end_time = time.time()
#     write_output_file(conf['output_file'], conf, data, start_time, end_time)

# if __name__ == "__main__":
#     run_experiment(conf)

import random
import time
import os
import sys
import socket
from schedcat.model.tasks import TaskSystem, SporadicTask
from rta import bound_response_times
from datetime import datetime

class Task(SporadicTask):
    def __init__(self, execution_time, period, deadline):
        super(Task, self).__init__(execution_time, period, deadline)
        self.jitter = 0
        self.suspended = 0
        self.prio_inversion = 0
        self.cost = execution_time

conf = {
    'experiment': 'rta_schedulability',
    'output_file': 'output/rta_schedulability.txt',
    'num_tasks': 10,           # Number of tasks per task set
    'samples': 5000,           # Number of task sets per utilization level
    'period_min': 10,          # Minimum task period
    'period_max': 100,         # Maximum task period
    'num_cpus': 1,             # Uniprocessor system
    'util_min': 0.1,           # Minimum utilization (expanded for better curve)
    'util_max': 1.0,           # Maximum utilization (expanded)
    'util_step': 0.05,         # Utilization step size (coarser for smoother results)
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
        cost = max(1, int(u * period))  # Ensure execution time is at least 1
        task = Task(cost, period, period)  # Implicit deadlines (deadline = period)
        taskset.append(task)
    
    taskset.sort_by_period()  # Sort by period for Rate Monotonic scheduling
    return taskset

def run_rta_test(taskset, num_cpus):
    return 1 if bound_response_times(num_cpus, taskset) else 0

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
            taskset = generate_task_set(conf, util)
            sched_sum += run_rta_test(taskset, conf['num_cpus'])
        sched_ratio = sched_sum / float(conf['samples'])
        data.append((util, sched_ratio))
        # print ("Utilization: {0:.2f}, Schedulability: {1:.2f}".format(util, sched_ratio))

    end_time = time.time()
    write_output_file(conf['output_file'], conf, data, start_time, end_time)

if __name__ == "__main__":
    run_experiment(conf)