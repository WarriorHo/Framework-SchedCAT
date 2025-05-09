from rta_nodrop import _event_residence_time_nodrop, SporadicTask

class TestTask(SporadicTask):
    def __init__(self, cost, period, syscall_count, priority, is_consumer=False):
        super(TestTask, self).__init__(cost, period)
        self.__dict__['syscall_count'] = syscall_count
        self.__dict__['priority'] = priority
        self.__dict__['is_consumer'] = is_consumer

delta = 0.1
alpha = 0.5
beta = 0.2

tau_1 = TestTask(cost=2.1, period=10, syscall_count=1, priority=1, is_consumer=False)
sigma_1 = TestTask(cost=0, period=10, syscall_count=1, priority=1, is_consumer=True)
tau_2 = TestTask(cost=3.2, period=15, syscall_count=2, priority=2, is_consumer=False)

higher_prio_tasks = [tau_1, sigma_1]

R_i, schedulable = _event_residence_time_nodrop(tau_2, higher_prio_tasks, delta, alpha, beta)
print("Event Residence Time R_2: {}".format(R_i))
print("Schedulable: {}".format(schedulable))