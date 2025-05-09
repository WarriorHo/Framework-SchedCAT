import random
from schedcat.model.tasks import SporadicTask, TaskSystem
import schedcat.generator.generator_emstada as emstada

PERIODS = { 
    '10-100': (10, 100),
}

class Config:
    def __init__(self):
        self.num_cpus = 4
        self.num_task = 100  # Small number for easy inspection
        self.util = 0.1    # Fixed utilization
        self.periods = '10-100'
        self.consumer_period_factor = 1.0
        self.consumer_syscall_count = 200

def generate_consumer_set(user_ts):
    for user_task in user_ts:
        consumer = SporadicTask(0,
            conf.consumer_period_factor * user_task.period,
            conf.consumer_period_factor * user_task.period)
        consumer.syscall_count = conf.consumer_syscall_count
        consumer.is_consumer = True
        consumer.partition = user_task.partition
        consumer.preemption_level = user_task.preemption_level - 0.5
        ts.append(consumer)
    return ts

def generate_task_set(conf):
    ts = TaskSystem()
    
    # Step 1: Generate user_tasks and assign to CPUs
    for cpuid in range(int(conf.num_cpus)):
        ntask = int(conf.num_task)
        u = float(conf.util)
        user_tasks = emstada.gen_taskset(PERIODS[conf.periods], 'unif', ntask, u, 0.01)
        for user_task in user_tasks:
            user_task.partition = cpuid
            user_task.syscall_count = 200
            user_task.is_consumer = False
            ts.append(user_task)
    
    # Step 2: Sort user_tasks by period and assign initial preemption levels
    user_ts = TaskSystem([t for t in ts if not t.is_consumer])
    user_ts.sort_by_period()
    for i, t in enumerate(user_ts):
        t.preemption_level = float(i)
    
    # Step 3: Generate corresponding consumer tasks
    # for user_task in user_ts:
    #     consumer = SporadicTask(0, conf.consumer_period_factor * user_task.period, conf.consumer_period_factor * user_task.period)
    #     consumer.syscall_count = conf.consumer_syscall_count
    #     consumer.is_consumer = True
    #     consumer.partition = user_task.partition
    #     consumer.preemption_level = user_task.preemption_level - 0.5
    #     ts.append(consumer)
    generate_consumer_set(user_ts)
    
    # Step 4: Sort all tasks by preemption_level and assign IDs
    ts.sort(key=lambda t: t.preemption_level)
    ts.assign_ids()
    
    return ts

def print_task_set(ts):
    """Print detailed information of the task set"""
    print("Task Set Details:")
    print("{:<5} {:<10} {:<5} {:<10} {:<20}".format('ID', 'Type', 'CPU', 'Period', 'Preemption Level'))
    print("-" * 50)
    for task in ts:
        task_type = "Consumer" if task.is_consumer else "User"
        print("{:<5} {:<10} {:<5} {:<10} {:<20}".format(
            task.id, 
            task_type, 
            task.partition, 
            task.period, 
            task.preemption_level
        ))
    print("\n")

if __name__ == "__main__":
    # Set random seed for reproducibility (optional)
    random.seed(42)
    
    # Create configuration
    conf = Config()
    
    # Generate and print task set
    task_set = generate_task_set(conf)
    print_task_set(task_set)
    print("Task Set Generation Complete.")