from schedcat.model.tasks import SporadicTask, TaskSystem
from rta_omnilog import bound_response_times_omnilog
from math import ceil
from params import AuditFramework, FRAMEWORKS, get_framework

tau1 = SporadicTask(2.3, 10, 10)
tau1.syscall_count = 1
tau1.preemption_level = 0
tau1.is_consumer = False

tau2 = SporadicTask(3.6, 15, 15)
tau2.syscall_count = 2
tau2.preemption_level = 1
tau2.is_consumer = False

consumer = SporadicTask(0, 10, 10)
consumer.is_consumer = True
consumer.preemption_level = -1

tasks = TaskSystem([tau1, tau2, consumer])

delta = 0.3
beta = 0.05

def test_bound_response_times_omnilog(num_cpus, tasks, delta, beta):
    tasks.sort(key=lambda t: t.preemption_level)
    consumer = next(t for t in tasks if t.is_consumer)
    q_sigma = consumer.period

    for t in tasks:
        t.response_time = 0
    
    def S(W):
        total_syscalls = 0
        for t in tasks:
            if not t.is_consumer:
                total_syscalls += ceil(float(W + t.response_time) / t.period) * t.syscall_count
        return total_syscalls
    
    iteration = 0
    converged = False
    while not converged:
        iteration += 1
        print("\n interation {}:".format(iteration))
        converged = True
        prev_r_sigma = consumer.response_time
        A_star = S(q_sigma + prev_r_sigma)
        print("\n A_star {}:".format(A_star))
        consumer_cost = beta * A_star
        consumer.response_time = consumer_cost
        print("  r_sigma: {:.2f}".format(consumer.response_time))
        if consumer.response_time != prev_r_sigma:
            converged = False
        
        for task in tasks:
            if not task.is_consumer:
                E_i = task.cost
                b_i = 0
                interference = 0
                for t in tasks:
                    if t.preemption_level < task.preemption_level and not t.is_consumer:
                        interference += ceil(float(task.response_time) / t.period) * t.cost
                I_sigma_i = ceil(float(task.response_time) / q_sigma) * beta * A_star
                new_r_i = E_i + b_i + interference + I_sigma_i
                if new_r_i != task.response_time:
                    task.response_time = new_r_i
                    converged = False
                print("  r_{}: {:.2f}".format(task.period, task.response_time))
    
    for t in tasks:
        if not t.is_consumer and t.response_time > t.deadline:
            return False
    return True

print("running bound_response_times_omnilog...")
is_schedulable = test_bound_response_times_omnilog(1, tasks, delta, beta)
print("\n whether is schedulable: {}".format(is_schedulable))