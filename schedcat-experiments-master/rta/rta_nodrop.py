# V1.0 #
# import math
# def is_schedulable_with_nodrop(task_system, num_processors, delta, alpha, beta):
#     normal_tasks = [t for t in task_system if not getattr(t, 'is_consumer', False)]
#     consumer_tasks = [t for t in task_system if getattr(t, 'is_consumer', False)]
#     all_tasks_sorted = sorted(task_system, key=lambda x: x.priority, reverse=True)
#     for task in normal_tasks:
#         E_i = task.exec_cost + task.syscall_count * delta    
#         r_i = E_i
#         prev_r_i = 0        
#         iteration = 0
#         max_iterations = 100        
#         while iteration < max_iterations and abs(r_i - prev_r_i) > 1e-6:
#             prev_r_i = r_i
#             total_interference = 0            
#             for hp_task in normal_tasks:
#                 if hp_task.priority > task.priority:
#                     E_k = hp_task.exec_cost + hp_task.syscall_count * delta
#                     interference = math.ceil(r_i / hp_task.period) * E_k
#                     total_interference += interference
#             for consumer in consumer_tasks:
#                 if consumer.priority > task.priority:
#                     C_consumer = alpha + consumer.syscall_count * beta
#                     q_k = consumer.period
#                     interference = math.ceil(r_i / q_k) * C_consumer
#                     total_interference += interference            
#             r_i = E_i + task.blocking_time + total_interference            
#             if r_i > task.deadline:
#                 return False            
#             iteration += 1        
#         if r_i > task.deadline:
#             return False    
#     return True

# V2.0 #
# import math
# def is_schedulable_with_nodrop(task_system, num_processors, delta, alpha, beta):
#     normal_tasks = [t for t in task_system if not getattr(t, 'is_consumer', False)]
#     consumer_tasks = [t for t in task_system if getattr(t, 'is_consumer', False)]
#     all_tasks = sorted(normal_tasks, key=lambda x: x.priority, reverse=True)
#     for task in all_tasks:
#         E_i = task.exec_cost + task.syscall_count * delta        
#         r_i = E_i + task.blocking_time
#         prev_r_i = 0
#         iteration = 0
#         max_iterations = 100        
#         while iteration < max_iterations and abs(r_i - prev_r_i) > 1e-6:
#             prev_r_i = r_i
#             total_interference = 0            
#             for hp_task in normal_tasks:
#                 if hp_task.priority > task.priority:
#                     E_k = hp_task.exec_cost + hp_task.syscall_count * delta
#                     interference = math.ceil(r_i / hp_task.period) * E_k
#                     total_interference += interference
#             for consumer in consumer_tasks:
#                 if consumer.priority > task.priority:
#                     interference = math.ceil(r_i / consumer.period) * consumer.exec_cost
#                     total_interference += interference            
#             r_i = E_i + task.blocking_time + total_interference            
#             if r_i > task.deadline:
#                 return False            
#             iteration += 1        
#         if r_i > task.deadline:
#             return False    
#     return True

# V3.0 #
# from __future__ import division
# from math import ceil

# def get_blocked(task):
#     return task.__dict__.get('blocked', 0)

# def get_jitter(task):
#     return task.__dict__.get('jitter', 0)

# def get_suspended(task):
#     return task.__dict__.get('suspended', 0)

# def get_prio_inversion(task):
#     return task.__dict__.get('prio_inversion', 0)

# def suspension_jitter(task):
#     if get_suspended(task) > 0:
#         return task.response_time - task.exec_cost
#     else:
#         return get_jitter(task)

# def _nodrop_rta(task, own_demand, higher_prio_tasks, hp_jitter, delta, alpha, beta):

#     max_iterations = 100
#     tolerance = 1e-6
    
#     normal_hp_tasks = [t for t in higher_prio_tasks if not getattr(t, 'is_consumer', False)]
#     consumer_hp_tasks = [t for t in higher_prio_tasks if getattr(t, 'is_consumer', False)]

#     r_i = own_demand + task.blocking_time
#     prev_r_i = 0
#     iteration = 0

#     while iteration < max_iterations and abs(r_i - prev_r_i) > tolerance:
#         prev_r_i = r_i
#         total_interference = 0

#         for hp in normal_hp_tasks:
#             E_k = hp.exec_cost + hp.syscall_count * delta
#             releases = ceil((r_i + hp_jitter(hp)) / hp.period)
#             total_interference += releases * E_k

#         for consumer in consumer_hp_tasks:
#             C_consumer = alpha + consumer.syscall_count * beta
#             releases = ceil((r_i + hp_jitter(consumer)) / consumer.period)
#             total_interference += releases * C_consumer

#         new_r_i = own_demand + task.blocking_time + total_interference
        
#         if new_r_i > task.deadline:
#             return False
#         if new_r_i == r_i:
#             break
            
#         r_i = new_r_i
#         iteration += 1

#     task.response_time = r_i + get_jitter(task)
#     return r_i <= task.deadline

# def bound_response_times_with_nodrop(no_cpus, taskset, delta, alpha, beta):

#     consumers = [t for t in taskset if getattr(t, 'is_consumer', False)]
#     normal_tasks = [t for t in taskset if not getattr(t, 'is_consumer', False)]
    
#     sorted_tasks = sorted(normal_tasks, key=lambda x: x.priority, reverse=True)
    
#     for idx, task in enumerate(sorted_tasks):

#         own_demand = (task.exec_cost + 
#                      task.syscall_count * delta + 
#                      get_prio_inversion(task))
        
#         higher_prio = sorted_tasks[0:idx] + consumers
        
#         if not _nodrop_rta(task, own_demand, higher_prio, get_jitter, delta, alpha, beta):
#             return False
#     return True

# is_schedulable_with_nodrop = lambda ts, np, d, a, b: bound_response_times_with_nodrop(np, ts, d, a, b)

# V4.0 #
from __future__ import division
from schedcat.model.tasks import TaskSystem, SporadicTask
from schedcat.model.consumers import create_consumers
from math import ceil

def get_blocked(task):
    return task.__dict__.get('blocked', 0)

def get_prio_inversion(task):
    return task.__dict__.get('prio_inversion', 0)

def get_syscall_count(task):
    return task.__dict__.get('syscall_count', 0)

def get_priority(task):
    return task.__dict__.get('priority', float('inf'))

def is_consumer_task(task):
    return task.__dict__.get('is_consumer', False)

def _calculate_total_execution_time(task, delta):
    return task.cost + get_syscall_count(task) * delta

def _calculate_audit_interference(task, higher_prio_consumers, r, alpha, beta):
    interference = 0
    for consumer in higher_prio_consumers:
        if is_consumer_task(consumer):
            interference += ceil(r / consumer.period) * (alpha + get_syscall_count(consumer) * beta)
    return interference

def _rta_nodrop(task, higher_prio_tasks, delta, alpha, beta):

    higher_prio_regular = [t for t in higher_prio_tasks if not is_consumer_task(t)]
    higher_prio_consumers = [t for t in higher_prio_tasks if is_consumer_task(t)]

    E_i = _calculate_total_execution_time(task, delta)
    b_i = get_prio_inversion(task)
    r = E_i + b_i + sum(t.cost for t in higher_prio_regular)
    
    while True:
        interference_regular = sum(ceil(r / t.period) * _calculate_total_execution_time(t, delta) for t in higher_prio_regular)
        interference_consumer = _calculate_audit_interference(task, higher_prio_consumers, r, alpha, beta)
        demand = E_i + b_i + interference_regular + interference_consumer
        if demand <= r:
            task.response_time = r
            return r <= task.deadline
        elif r > task.deadline:
            return False
        else:
            r = demand

# Event Residence Time
def _event_residence_time_nodrop(task, higher_prio_tasks, delta, alpha, beta):
    
    higher_prio_regular = [t for t in higher_prio_tasks if not is_consumer_task(t)]
    higher_prio_consumers = [t for t in higher_prio_tasks if is_consumer_task(t)]
    
    T_w = task.period
    T_p_base = alpha + get_syscall_count(task) * beta
    T_p = T_p_base + sum(t.cost for t in higher_prio_regular)
    
    while True:
        interference_regular = sum(ceil(T_p / t.period) * t.cost for t in higher_prio_regular)
        interference_consumer = _calculate_audit_interference(task, higher_prio_consumers, T_p, alpha, beta)
        demand = T_p_base + interference_regular + interference_consumer
        if demand <= T_p:
            T_p = demand
            break
        else:
            T_p = demand
    R_i = T_w + T_p
    
    return R_i, R_i <= task.deadline


def bound_response_times_nodrop(tasks, delta, alpha, beta):
    tasks.sort(key=get_priority)
    for i, task in enumerate(tasks):
        if not _rta_nodrop(task, tasks[:i], delta, alpha, beta):
            return False
    return True

def is_schedulable_with_nodrop(tasks, num_processors, delta, alpha, beta, qk_ratio=1.0):
    consumers = create_consumers(tasks, alpha, beta, qk_ratio)
    full_system = TaskSystem(tasks + consumers)
    full_system.sort(key=get_priority)
    if num_processors == 1:
        return bound_response_times_nodrop(full_system, delta, alpha, beta)
    else:
        processors = [TaskSystem() for _ in range(num_processors)]
        for i, task in enumerate(full_system):
            processors[i % num_processors].append(task)
        for proc_tasks in processors:
            if not bound_response_times_nodrop(proc_tasks, delta, alpha, beta):
                return False
        return True

is_schedulable = is_schedulable_with_nodrop