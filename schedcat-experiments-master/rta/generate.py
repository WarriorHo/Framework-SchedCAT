import random
from rta import bound_response_times

class Task:
    def __init__(self):
        self.cost = 0
        self.period = 0
        self.deadline = 0
        self.jitter = 0
        self.suspended = 0

def generate_task_set(conf):
    taskset = []
    total_util = conf['util'] * conf['num_cpus']
    for _ in range(conf['num_task']):
        task = Task()
        task.period = random.randint(conf['period_min'], conf['period_max'])
        task.deadline = task.period
        task.cost = int(total_util / conf['num_task'] * task.period)
        task.jitter = 0
        task.suspended = 0
        taskset.append(task)
    taskset.sort(key=lambda t: t.period)
    return taskset

def run_rta_test(taskset, num_cpus, conf):
    is_sched = bound_response_times(num_cpus, taskset)
    return int(is_sched), 0