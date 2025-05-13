# 1 consumer number

Omnilog采用单一高优先级消费者任务运行在专用核心上，避免了多消费者任务间的优先级反转和资源竞争

Nodrop为每个线程分配独立消费者，导致多消费者任务间的干扰

# 2 consumer period

Omnilog的周期固定为 min q_k）能及时抢占其他任务

Nodrop的周期可以选择为 n * q_k 可能因线程优先级差异引入调度延迟

# 3 interference

Omnilog的干扰仅来自全局消费者任务，忽略了多次 alpha

Nodrop需考虑每个线程的消费者任务叠加干扰，每次都需要加上alpha