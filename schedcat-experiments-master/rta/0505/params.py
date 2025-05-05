from __future__ import division

class AuditFramework:
    def __init__(self, name, delta=None, alpha=None, beta=None):
        self.name = name
        self.delta = delta
        self.alpha = alpha
        self.beta = beta

    def calculate_execution_time(self, task):
        if self.name == 'rta':
            return task.cost
        elif self.name == 'omnilog':
            if self.delta is None:
                raise ValueError("Delta parameter required for omnilog framework")
            return task.cost + task.syscall_count * self.delta
        elif self.name == 'nodrop':
            if self.delta is None or self.alpha is None or self.beta is None:
                raise ValueError("Delta, alpha, and beta parameters required for nodrop framework")
            if task.is_consumer:
                return self.alpha + task.syscall_count * self.beta
            else:
                return task.cost + task.syscall_count * self.delta
        else:
            raise ValueError("Unknown framework: {}".format(self.name))

FRAMEWORKS = {
    'rta': AuditFramework('rta'),
    'omnilog': AuditFramework('omnilog', delta=0.3),
    'nodrop': AuditFramework('nodrop', delta=0.1, alpha=0.2, beta=0.05)
}

def get_framework(framework_name):
    if framework_name not in FRAMEWORKS:
        raise ValueError("Framework {} not found".format(framework_name))
    return FRAMEWORKS[framework_name]