from __future__ import division
from math import ceil

def get_syscall_count(task):
    return task.__dict__.get('syscall_count', 0)

def get_blocked(task):
    return task.__dict__.get('blocked', 0)

def get_jitter(task):
    return task.__dict__.get('jitter', 0)

def get_suspended(task):
    return task.__dict__.get('suspended', 0)

def get_prio_inversion(task):
    return task.__dict__.get('prio_inversion', 0)

def suspension_jitter(task):
    if get_suspended(task) > 0:
        # Suspension to jitter reduction: max jitter is R_i - C_i
        return task.response_time - task.cost
    else:
        return get_jitter(task)

# def _calculate_total_execution_time(task, delta):
#     return task.cost + get_syscall_count(task) * delta

def _rta_omnilog(task, own_demand, higher_prio_tasks, hp_jitter, delta):
    total_demand = sum(t.cost for t in higher_prio_tasks) + own_demand
    while total_demand <= task.deadline:
        demand = own_demand
        for t in higher_prio_tasks:
            demand += t.cost * int(ceil((total_demand + hp_jitter(t)) / t.period))
        if demand == total_demand:
            task.response_time = total_demand + get_jitter(task)
            return True
        else:
            total_demand = demand
    return False

# def rta_omnilog_jitter_aware(task, higher_prio_tasks, delta):
#     own_demand = get_prio_inversion(task) + _calculate_total_execution_time(task, delta)
#     return _rta_omnilog(task, own_demand, higher_prio_tasks, get_jitter, delta)

def rta_omnilog_jitter_aware(task, higher_prio_tasks, delta):
    own_demand = get_prio_inversion(task) + task.cost
    return _rta_omnilog(task, own_demand, higher_prio_tasks, get_jitter, delta)

# def rta_omnilog_suspension_aware(task, higher_prio_tasks, delta):
#     own_demand = get_prio_inversion(task) + _calculate_total_execution_time(task, delta) + get_suspended(task)
#     return _rta_omnilog(task, own_demand, higher_prio_tasks, suspension_jitter, delta)

def rta_omnilog_suspension_aware(task, higher_prio_tasks, delta):
    own_demand = get_prio_inversion(task) + task.cost + get_suspended(task)
    return _rta_omnilog(task, own_demand, higher_prio_tasks, suspension_jitter, delta)

# def legacy_rta_omnilog_jitter_aware(task, higher_prio_tasks, delta):
#     own_demand = get_blocked(task) + _calculate_total_execution_time(task, delta)
#     return _rta_omnilog(task, own_demand, higher_prio_tasks, get_jitter)

def legacy_rta_omnilog_jitter_aware(task, higher_prio_tasks, delta):
    own_demand = get_blocked(task) + task.cost
    return _rta_omnilog(task, own_demand, higher_prio_tasks, get_jitter)

# def legacy_rta_suspension_aware(task, higher_prio_tasks, delta):
#     own_demand = get_blocked(task) + _calculate_total_execution_time(task, delta)
#     return _rta_omnilog(task, own_demand, higher_prio_tasks, suspension_jitter)

def legacy_rta_suspension_aware(task, higher_prio_tasks, delta):
    own_demand = get_blocked(task) + task.cost
    return _rta_omnilog(task, own_demand, higher_prio_tasks, suspension_jitter)

def has_self_suspensions(taskset):
    for t in taskset:
        if 'suspended' in t.__dict__ and t.suspended != 0:
            return True
    return False

def uses_legacy_blocked_field(taskset):
    for t in taskset:
        if 'blocked' in t.__dict__:
            return True
    return False

def bound_response_times_omnilog(no_cpus, taskset, delta):
    legacy = uses_legacy_blocked_field(taskset)
    susp   = has_self_suspensions(taskset)
    if not (no_cpus == 1 and taskset.only_constrained_deadlines()):
        return False
    
    rta = rta_omnilog_suspension_aware if susp else rta_omnilog_jitter_aware
    
    for i, task in enumerate(taskset):
        if not rta(task, taskset[0:i], delta):
            return False
    return True

is_schedulable_with_omnilog = bound_response_times_omnilog