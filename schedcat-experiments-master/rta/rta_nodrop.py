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

# cpu

# def _rta_nodrop(task, higher_prio_tasks, delta, alpha, beta):

#     higher_prio_regular = [t for t in higher_prio_tasks if not is_consumer_task(t)]
#     higher_prio_consumers = [t for t in higher_prio_tasks if is_consumer_task(t)]

#     E_i = _calculate_total_execution_time(task, delta)
#     b_i = get_prio_inversion(task)
#     r = E_i + b_i + sum(t.cost for t in higher_prio_regular)
    
#     while True:
#         interference_regular = sum(ceil(r / t.period) * _calculate_total_execution_time(t, delta) for t in higher_prio_regular)
#         interference_consumer = _calculate_audit_interference(task, higher_prio_consumers, r, alpha, beta)
#         demand = E_i + b_i + interference_regular + interference_consumer
#         if demand <= r:
#             task.response_time = r
#             return r <= task.deadline
#         elif r > task.deadline:
#             return False
#         else:
#             r = demand

def _rta_nodrop(task, higher_prio_tasks, delta, alpha, beta):
    higher_prio_regular = [t for t in higher_prio_tasks if not is_consumer_task(t)]
    higher_prio_consumers = [t for t in higher_prio_tasks if is_consumer_task(t)]

    E_i = task.cost
    b_i = get_prio_inversion(task)
    r = E_i + b_i + sum(t.cost for t in higher_prio_regular)
    
    # add iteration
    iteration = 0

    while True:

        # add interation
        iteration += 1
        print("\n _rta_nodrop Task {} Iteration {}: ".format(task.id, iteration))
        print("  r_old: {:.2f}".format(r))

        interference_regular = sum(ceil(float(r) / t.period) * t.cost for t in higher_prio_regular)
        # add print
        print("  interference_regular: {:.2f}".format(interference_regular))

        interference_consumer = sum(ceil(float(r) / c.period) * c.cost for c in higher_prio_consumers)
        # add print
        print("  interference_consumer: {:.2f}".format(interference_consumer))
        
        demand = E_i + b_i + interference_regular + interference_consumer
        # add print
        print("  demand: {:.2f}".format(demand))
        
        if demand <= r:
            task.response_time = r
            # add print
            print("  converged r: {:.2f}".format(r))
            return r <= task.deadline
        elif r > task.deadline:
            print("  missed deadline: r ({:.2f}) > deadline ({})".format(r, task.deadline))
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
    
    # return R_i, R_i <= task.deadline
    return R_i


def bound_response_times_nodrop(tasks, delta, alpha, beta):
    tasks.sort(key=get_priority)
    for i, task in enumerate(tasks):
        
        # add print
        print("\n Nodrop on Task {} (priority {}):".format(task.id, get_priority(task)))
        higher = tasks[:i]
        print("  Higher-prio tasks: {}".format([t.id for t in higher]))
        
        # add print
        schedulable = _rta_nodrop(task, higher, delta, alpha, beta)
        print("  Task {} schedulable: {}\n".format(task.id, schedulable))
        if not schedulable:
            return False

        # if not _rta_nodrop(task, tasks[:i], delta, alpha, beta):
            # return False

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