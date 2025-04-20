# V1.0 #
# import random
# import time
# import os
# import sys
# from rta import bound_response_times

# class Task:
#     def __init__(self):
#         self.cost = 0
#         self.period = 0
#         self.deadline = 0
#         self.jitter = 0
#         self.suspended = 0

# conf = {
#     'experiment': 'util_num',
#     'output_file': 'output/util_num/rn=10_wl=100_wn=10_c=20_rl=100',
#     'num_task': 10,
#     'samples': 500,
#     'periods': '10-100',
#     'period_min': 10,
#     'period_max': 100,
#     'num_cpus': 20,
#     'num_reads': 10,
#     'num_writes': 10,
#     'read_len': 100,
#     'write_len': 100,
#     'num_mem': 1,
#     'step': 0.03,
#     'util_num_min': 0.6,
#     'util_num_max': 0.92,
# }

# def generate_task_set(conf):
#     taskset = []
#     total_util = conf['util'] * conf['num_cpus']
#     for _ in range(conf['num_task']):
#         task = Task()
#         task.period = random.randint(conf['period_min'], conf['period_max'])
#         task.deadline = task.period
#         task.cost = int(total_util / conf['num_task'] * task.period)
#         task.jitter = 0
#         task.suspended = 0
#         taskset.append(task)
#     taskset.sort(key=lambda t: t.period)
#     return taskset

# def run_rta_test(taskset, num_cpus, conf):
#     is_sched = bound_response_times(num_cpus, taskset)
#     return int(is_sched), 0

# def write_output_file(output_file, conf, data, start_time, end_time):
#     with open(output_file, 'w') as f:
#         f.write("############################### CONFIGURATION ################################\n")
#         for key, value in conf.items():
#             f.write(f"# {key.ljust(15)}: {value}\n")
#         f.write("################################ ENVIRONMENT #################################\n")
#         f.write(f"# Version........: <unknown>\n")
#         f.write(f"# CWD............: {os.getcwd()}\n")
#         f.write(f"# Host...........: {os.uname().nodename}\n")
#         f.write(f"# Python.........: {sys.version}\n")
#         f.write("#################################### DATA ####################################\n")
#         f.write("#  UTILIZATION  #rta\n")
#         for util, sched in data:
#             f.write(f"{util:>14.2f} {sched:>6.2f} 0.00\n")
#         f.write("#################################### RUN #####################################\n")
#         f.write(f"# Started........: {start_time}\n")
#         f.write(f"# Completed......: {end_time}\n")
#         f.write(f"# Duration.......: {end_time - start_time}\n")

# def run_util_experiment(conf):
#     start_time = time.time()
#     data = []
#     util_min = conf['util_num_min']
#     util_max = conf['util_num_max']
#     step = conf['step']
#     num_samples = conf['samples']
    
#     for util in [util_min + i * step for i in range(int((util_max - util_min) / step) + 1)]:
#         sched_sum = 0
#         for _ in range(num_samples):
#             conf['util'] = util
#             taskset = generate_task_set(conf)
#             sched, _ = run_rta_test(taskset, conf['num_cpus'], conf)
#             sched_sum += sched
#         sched_avg = sched_sum / num_samples
#         data.append((util, sched_avg))
    
#     end_time = time.time()
#     write_output_file(conf['output_file'], conf, data, start_time, end_time)

# run_util_experiment(conf)

# V2.0 #
# import random
# import time
# import os
# import sys
# from rta import bound_response_times

# class Task:
#     def __init__(self):
#         self.cost = 0
#         self.period = 0
#         self.deadline = 0
#         self.jitter = 0
#         self.suspended = 0

# conf = {
#     'experiment': 'util_num',
#     'output_file': 'output/util_num/rn=10_wl=100_wn=10_c=20_rl=100',
#     'num_task': 10,
#     'samples': 500,
#     'periods': '10-100',
#     'period_min': 10,
#     'period_max': 100,
#     'num_cpus': 20,
#     'num_reads': 10,
#     'num_writes': 10,
#     'read_len': 100,
#     'write_len': 100,
#     'num_mem': 1,
#     'step': 0.03,
#     'util_num_min': 0.6,
#     'util_num_max': 0.92,
# }

# def generate_task_set(conf):
#     taskset = []
#     total_util = conf['util'] * conf['num_cpus']
#     for _ in range(conf['num_task']):
#         task = Task()
#         task.period = random.randint(conf['period_min'], conf['period_max'])
#         task.deadline = task.period
#         task.cost = int(total_util / conf['num_task'] * task.period)
#         task.jitter = 0
#         task.suspended = 0
#         taskset.append(task)
#     taskset.sort(key=lambda t: t.period)
#     return taskset

# def run_rta_test(taskset, num_cpus, conf):
#     is_sched = bound_response_times(num_cpus, taskset)
#     return int(is_sched), 0

# def write_output_file(output_file, conf, data, start_time, end_time):
#     with open(output_file, 'w') as f:
#         f.write("############################### CONFIGURATION ################################\n")
#         for key, value in conf.items():
#             f.write("# {}: {}\n".format(key.ljust(15), value))
#         f.write("################################ ENVIRONMENT #################################\n")
#         f.write("# Version........: {}\n".format("<unknown>"))
#         f.write("# CWD............: {}\n".format(os.getcwd()))
#         f.write("# Host...........: {}\n".format(os.uname().nodename))
#         f.write("# Python.........: {}\n".format(sys.version))
#         f.write("#################################### DATA ####################################\n")
#         f.write("#  UTILIZATION  #rta\n")
#         for util, sched in data:
#             f.write("{:>14.2f} {:>6.2f} 0.00\n".format(util, sched))
#         f.write("#################################### RUN #####################################\n")
#         f.write("# Started........: {}\n".format(start_time))
#         f.write("# Completed......: {}\n".format(end_time))
#         f.write("# Duration.......: {}\n".format(end_time - start_time))

# def run_util_experiment(conf):
#     start_time = time.time()
#     data = []
#     util_min = conf['util_num_min']
#     util_max = conf['util_num_max']
#     step = conf['step']
#     num_samples = conf['samples']
    
#     for util in [util_min + i * step for i in range(int((util_max - util_min) / step) + 1)]:
#         sched_sum = 0
#         for _ in range(num_samples):
#             conf['util'] = util
#             taskset = generate_task_set(conf)
#             sched, _ = run_rta_test(taskset, conf['num_cpus'], conf)
#             sched_sum += sched
#         sched_avg = sched_sum / num_samples
#         data.append((util, sched_avg))
    
#     end_time = time.time()
#     write_output_file(conf['output_file'], conf, data, start_time, end_time)

# run_util_experiment(conf)

# V3.0 #
# import random
# import time
# import os
# import sys
# import socket
# from rta import bound_response_times

# class Task:
#     def __init__(self):
#         self.cost = 0
#         self.period = 0
#         self.deadline = 0
#         self.jitter = 0
#         self.suspended = 0

# conf = {
#     'experiment': 'util_num',
#     'output_file': 'output/util_num/rn=10_wl=100_wn=10_c=20_rl=100',
#     'num_task': 10,
#     'samples': 500,
#     'periods': '10-100',
#     'period_min': 10,
#     'period_max': 100,
#     'num_cpus': 20,
#     'num_reads': 10,
#     'num_writes': 10,
#     'read_len': 100,
#     'write_len': 100,
#     'num_mem': 1,
#     'step': 0.03,
#     'util_num_min': 0.6,
#     'util_num_max': 0.92,
# }

# def generate_task_set(conf):
#     taskset = []
#     total_util = conf['util'] * conf['num_cpus']
#     for _ in range(conf['num_task']):
#         task = Task()
#         task.period = random.randint(conf['period_min'], conf['period_max'])
#         task.deadline = task.period
#         task.cost = int(total_util / conf['num_task'] * task.period)
#         task.jitter = 0
#         task.suspended = 0
#         taskset.append(task)
#     taskset.sort(key=lambda t: t.period)
#     return taskset

# def run_rta_test(taskset, num_cpus, conf):
#     is_sched = bound_response_times(num_cpus, taskset)
#     return int(is_sched), 0

# def write_output_file(output_file, conf, data, start_time, end_time):
#     with open(output_file, 'w') as f:
#         f.write("############################### CONFIGURATION ################################\n")
#         for key, value in conf.items():
#             f.write("# {}: {}\n".format(key.ljust(15), value))
#         f.write("################################ ENVIRONMENT #################################\n")
#         f.write("# Version........: {}\n".format("<unknown>"))
#         f.write("# CWD............: {}\n".format(os.getcwd()))
#         f.write("# Host...........: {}\n".format(socket.gethostname()))
#         f.write("# Python.........: {}\n".format(sys.version))
#         f.write("#################################### DATA ####################################\n")
#         f.write("#  UTILIZATION  #rta\n")
#         for util, sched in data:
#             f.write("{:>14.2f} {:>6.2f} 0.00\n".format(util, sched))
#         f.write("#################################### RUN #####################################\n")
#         f.write("# Started........: {}\n".format(start_time))
#         f.write("# Completed......: {}\n".format(end_time))
#         f.write("# Duration.......: {}\n".format(end_time - start_time))

# def run_util_experiment(conf):
#     start_time = time.time()
#     data = []
#     util_min = conf['util_num_min']
#     util_max = conf['util_num_max']
#     step = conf['step']
#     num_samples = conf['samples']
    
#     for util in [util_min + i * step for i in range(int((util_max - util_min) / step) + 1)]:
#         sched_sum = 0
#         for _ in range(num_samples):
#             conf['util'] = util
#             taskset = generate_task_set(conf)
#             sched, _ = run_rta_test(taskset, conf['num_cpus'], conf)
#             sched_sum += sched
#         sched_avg = sched_sum / num_samples
#         data.append((util, sched_avg))
    
#     end_time = time.time()
#     write_output_file(conf['output_file'], conf, data, start_time, end_time)

# run_util_experiment(conf)

# V4.0 #
# import random
# import time
# import os
# import sys
# from rta import bound_response_times
# from schedcat.model.tasks import TaskSystem

# class Task:
#     def __init__(self):
#         self.cost = 0
#         self.period = 0
#         self.deadline = 0
#         self.jitter = 0
#         self.suspended = 0
#         self.cpu = 0

# conf = {
#     'experiment': 'util_num',
#     'output_file': 'output/util_num/rn=10_wl=100_wn=10_c=20_rl=100',
#     'num_task': 10,
#     'samples': 500,
#     'periods': '10-100',
#     'period_min': 10,
#     'period_max': 100,
#     'num_cpus': 20,
#     'num_reads': 10,
#     'num_writes': 10,
#     'read_len': 100,
#     'write_len': 100,
#     'num_mem': 1,
#     'step': 0.03,
#     'util_num_min': 0.6,
#     'util_num_max': 0.92,
# }

# def generate_task_set(conf):
#     taskset = []
#     tasks_per_cpu = conf['num_task']
#     util_per_cpu = conf['util']
    
#     for cpu in range(conf['num_cpus']):
#         for _ in range(tasks_per_cpu):
#             task = Task()
#             task.cpu = cpu
#             task.period = random.randint(conf['period_min'], conf['period_max'])
#             task.deadline = task.period
#             task.cost = int((util_per_cpu / tasks_per_cpu) * task.period)
#             task.jitter = 0
#             task.suspended = 0
#             taskset.append(task)
#     return taskset

# def run_rta_test(taskset, num_cpus, conf):
#     schedulable = True
#     for cpu in range(num_cpus):
#         cpu_tasks = [t for t in taskset if t.cpu == cpu]
#         if not bound_response_times(1, cpu_tasks):
#             schedulable = False
#             break
#     return int(schedulable), 0

# def write_output_file(output_file, conf, data, start_time, end_time):
#     with open(output_file, 'w') as f:
#         f.write("############################### CONFIGURATION ################################\n")
#         for key, value in conf.items():
#             f.write("# {0:<15}: {1}\n".format(key, value))

#         f.write("################################ ENVIRONMENT #################################\n")
#         f.write("# Version........: <unknown>\n")
#         f.write("# CWD............: {0}\n".format(os.getcwd()))
#         f.write("# Host...........: {0}\n".format(os.uname().nodename))
#         f.write("# Python.........: {0}\n".format(sys.version))

#         f.write("#################################### DATA ####################################\n")
#         f.write("#  UTILIZATION  #rta\n")
#         for util, sched in data:
#             f.write("{0:>14.2f} {1:>6.2f} 0.00\n".format(util, sched))

#         f.write("#################################### RUN #####################################\n")
#         f.write("# Started........: {0}\n".format(start_time))
#         f.write("# Completed......: {0}\n".format(end_time))
#         f.write("# Duration.......: {0}\n".format(end_time - start_time))

# def run_util_experiment(conf):
#     start_time = time.time()
#     data = []
#     util_min = conf['util_num_min']
#     util_max = conf['util_num_max']
#     step = conf['step']
#     num_samples = conf['samples']
    
#     for util in [util_min + i * step for i in range(int((util_max - util_min) / step) + 1)]:
#         sched_sum = 0
#         for _ in range(num_samples):
#             conf['util'] = util
#             taskset = generate_task_set(conf)
#             sched, _ = run_rta_test(taskset, conf['num_cpus'], conf)
#             sched_sum += sched
#         sched_avg = sched_sum / num_samples
#         data.append((util, sched_avg))
    
#     end_time = time.time()
#     write_output_file(conf['output_file'], conf, data, start_time, end_time)

# run_util_experiment(conf)

# V5.0 #
import random
import time
import os
import sys
from rta import bound_response_times
from schedcat.model.tasks import TaskSystem, SporadicTask

class Task(SporadicTask):
    def __init__(self, cost, period, deadline, cpu):
        super(Task, self).__init__(cost, period, deadline)
        self.jitter = 0
        self.suspended = 0
        self.cpu = cpu
        
conf = {
    'experiment': 'util_num',
    'output_file': 'output/util_num/rn=10_wl=100_wn=10_c=20_rl=100',
    'num_task': 10,
    'samples': 500,
    'periods': '10-100',
    'period_min': 10,
    'period_max': 100,
    'num_cpus': 20,
    'num_reads': 10,
    'num_writes': 10,
    'read_len': 100,
    'write_len': 100,
    'num_mem': 1,
    'step': 0.03,
    'util_num_min': 0.6,
    'util_num_max': 0.92,
}

def generate_task_set(conf):
    taskset = TaskSystem()
    tasks_per_cpu = conf['num_task']
    util_per_cpu = conf['util']
    
    for cpu in range(conf['num_cpus']):
        for _ in range(tasks_per_cpu):
            period = random.randint(conf['period_min'], conf['period_max'])
            cost = int((util_per_cpu / tasks_per_cpu) * period)
            task = Task(cost, period, period, cpu)
            taskset.append(task)
    return taskset

def run_rta_test(taskset, num_cpus, conf):
    schedulable = True
    for cpu in range(num_cpus):
        cpu_tasks = TaskSystem([t for t in taskset if t.cpu == cpu])
        if not bound_response_times(1, cpu_tasks):
            schedulable = False
            break
    return int(schedulable), 0

def write_output_file(output_file, conf, data, start_time, end_time):
    with open(output_file, 'w') as f:
        f.write("############################### CONFIGURATION ################################\n")
        for key, value in conf.items():
            f.write("# {0:<15}: {1}\n".format(key, value))

        f.write("################################ ENVIRONMENT #################################\n")
        f.write("# Version........: <unknown>\n")
        f.write("# CWD............: {0}\n".format(os.getcwd()))
        f.write("# Host...........: {0}\n".format(os.uname().nodename))
        f.write("# Python.........: {0}\n".format(sys.version))

        f.write("#################################### DATA ####################################\n")
        f.write("#  UTILIZATION  #rta\n")
        for util, sched in data:
            f.write("{0:>14.2f} {1:>6.2f} 0.00\n".format(util, sched))

        f.write("#################################### RUN #####################################\n")
        f.write("# Started........: {0}\n".format(start_time))
        f.write("# Completed......: {0}\n".format(end_time))
        f.write("# Duration.......: {0}\n".format(end_time - start_time))

def run_util_experiment(conf):
    start_time = time.time()
    data = []
    util_min = conf['util_num_min']
    util_max = conf['util_num_max']
    step = conf['step']
    num_samples = conf['samples']
    
    for util in [util_min + i * step for i in range(int((util_max - util_min) / step) + 1)]:
        sched_sum = 0
        for _ in range(num_samples):
            conf['util'] = util
            taskset = generate_task_set(conf)
            sched, _ = run_rta_test(taskset, conf['num_cpus'], conf)
            sched_sum += sched
        sched_avg = sched_sum / num_samples
        data.append((util, sched_avg))
    
    end_time = time.time()
    write_output_file(conf['output_file'], conf, data, start_time, end_time)

run_util_experiment(conf)