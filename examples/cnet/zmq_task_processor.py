import asyncio
import json
import random
import time
import uuid
from enum import Enum

from sdk.cnet import TCPSocketParameters, ZMQDealer, ZMQRouter

# Router (task manager) socket parameters
ROUTER_TCP_PARAMETERS = TCPSocketParameters(host="localhost", port=5558)

# Number of worker clients to simulate
NUM_WORKERS = 3
# Number of client tasks to generate
NUM_TASKS = 10


class TaskStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Task:
    def __init__(self, task_id=None, complexity=None):
        self.task_id = task_id or str(uuid.uuid4())
        # Complexity determines how long the task takes (1-10)
        self.complexity = complexity or random.randint(1, 10)
        self.status = TaskStatus.PENDING
        self.result = None
        self.worker_id = None
        self.created_at = time.time()
        self.completed_at = None

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "complexity": self.complexity,
            "status": self.status.value,
            "result": self.result,
            "worker_id": self.worker_id,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }

    @classmethod
    def from_dict(cls, data):
        task = cls(task_id=data["task_id"], complexity=data["complexity"])
        task.status = TaskStatus(data["status"])
        task.result = data.get("result")
        task.worker_id = data.get("worker_id")
        task.created_at = data.get("created_at", time.time())
        task.completed_at = data.get("completed_at")
        return task

    def __str__(self):
        return f"Task {self.task_id[:8]} (complexity: {self.complexity}, status: {self.status.value})"


async def task_manager_coro():
    """Router socket that manages tasks and distributes them to workers"""
    print("Starting task manager...")
    tasks = {}
    workers = set()

    # Profiling variables
    message_count = 0
    start_time = time.time()
    last_profile_time = start_time

    # Create initial tasks
    for _ in range(NUM_TASKS):
        task = Task()
        tasks[task.task_id] = task
        print(f"Created {task}")

    async with ZMQRouter(ROUTER_TCP_PARAMETERS) as router:
        while True:
            # Receive message from any worker or client
            message = await router.recv_multipart()
            sender_id = message[0]
            content = json.loads(message[2].decode())

            # Update message count for profiling
            message_count += 1
            current_time = time.time()
            elapsed = current_time - last_profile_time

            # Print profiling info every second
            if elapsed >= 1.0:
                total_elapsed = current_time - start_time
                msg_per_sec = message_count / total_elapsed if total_elapsed > 0 else 0
                print(
                    f"Performance: {msg_per_sec:.2f} messages/second (total: {message_count})"
                )
                last_profile_time = current_time

            msg_type = content.get("type")

            if msg_type == "worker_ready":
                # Worker is ready for tasks
                worker_id = content.get("worker_id")
                workers.add(worker_id)
                print(f"Worker {worker_id} is ready")

                # Find a pending task
                pending_tasks = [
                    t for t in tasks.values() if t.status == TaskStatus.PENDING
                ]
                if pending_tasks:
                    task = pending_tasks[0]
                    task.status = TaskStatus.PROCESSING
                    task.worker_id = worker_id

                    # Send task to worker
                    response = {"type": "task_assigned", "task": task.to_dict()}
                    print(f"Assigning {task} to worker {worker_id}")
                    await router.send_multipart(
                        [sender_id, b"", json.dumps(response).encode()]
                    )
                else:
                    # No tasks available
                    response = {"type": "no_tasks"}
                    await router.send_multipart(
                        [sender_id, b"", json.dumps(response).encode()]
                    )

            elif msg_type == "task_completed":
                # Worker completed a task
                task_data = content.get("task")
                task = Task.from_dict(task_data)

                if task.task_id in tasks:
                    tasks[task.task_id].status = TaskStatus.COMPLETED
                    tasks[task.task_id].result = task.result
                    tasks[task.task_id].completed_at = task.completed_at
                    print(
                        f"Task {task.task_id[:8]} completed by worker {task.worker_id}"
                    )

                # Send acknowledgment
                response = {"type": "ack"}
                await router.send_multipart(
                    [sender_id, b"", json.dumps(response).encode()]
                )

                # Check if all tasks are completed
                if all(t.status == TaskStatus.COMPLETED for t in tasks.values()):
                    print("\nAll tasks completed!")
                    for task_id, task in tasks.items():
                        elapsed = task.completed_at - task.created_at
                        print(
                            f"Task {task_id[:8]}: complexity {task.complexity}, "
                            f"completed in {elapsed:.2f}s by worker {task.worker_id}"
                        )

                    # Create some new tasks
                    for _ in range(random.randint(1, 3)):
                        task = Task()
                        tasks[task.task_id] = task
                        print(f"Created new {task}")

            elif msg_type == "task_failed":
                # Worker failed to complete a task
                task_data = content.get("task")
                task = Task.from_dict(task_data)

                if task.task_id in tasks:
                    tasks[task.task_id].status = TaskStatus.FAILED
                    print(f"Task {task.task_id[:8]} failed by worker {task.worker_id}")

                # Send acknowledgment
                response = {"type": "ack"}
                await router.send_multipart(
                    [sender_id, b"", json.dumps(response).encode()]
                )


async def worker_coro(worker_id):
    """Worker that processes tasks from the task manager"""
    worker_name = f"worker-{worker_id}"
    print(f"Starting {worker_name}...")

    # Profiling variables
    message_count = 0
    start_time = time.time()
    last_profile_time = start_time

    async with ZMQDealer(ROUTER_TCP_PARAMETERS) as dealer:
        while True:
            # Signal that we're ready for work
            request = {"type": "worker_ready", "worker_id": worker_name}
            await dealer.send_multipart([b"", json.dumps(request).encode()])

            # Update message count for profiling
            message_count += 1

            # Wait for a task
            response = await dealer.recv_multipart()
            content = json.loads(response[1].decode())

            # Update message count for profiling
            message_count += 1
            current_time = time.time()
            elapsed = current_time - last_profile_time

            # Print profiling info every second
            if elapsed >= 1.0:
                total_elapsed = current_time - start_time
                msg_per_sec = message_count / total_elapsed if total_elapsed > 0 else 0
                print(
                    f"Worker {worker_name}: {msg_per_sec:.2f} messages/second (total: {message_count})"
                )
                last_profile_time = current_time

            msg_type = content.get("type")

            if msg_type == "task_assigned":
                # Process the task
                task_data = content.get("task")
                task = Task.from_dict(task_data)

                print(
                    f"{worker_name} processing task {task.task_id[:8]} (complexity: {task.complexity})"
                )

                # Simulate work based on task complexity
                try:
                    # Simulate work with potential for failure
                    work_time = task.complexity * 0.5
                    await asyncio.sleep(work_time)

                    # 10% chance of failure for complex tasks
                    if task.complexity > 7 and random.random() < 0.1:
                        raise Exception("Task failed")

                    # Task completed successfully
                    task.status = TaskStatus.COMPLETED
                    task.result = (
                        f"Result from {worker_name}: {random.randint(1000, 9999)}"
                    )
                    task.completed_at = time.time()

                    # Send completion notification
                    completion = {"type": "task_completed", "task": task.to_dict()}
                    await dealer.send_multipart([b"", json.dumps(completion).encode()])
                    message_count += 1

                except Exception as e:
                    # Task failed
                    task.status = TaskStatus.FAILED
                    task.result = str(e)

                    # Send failure notification
                    failure = {"type": "task_failed", "task": task.to_dict()}
                    await dealer.send_multipart([b"", json.dumps(failure).encode()])
                    message_count += 1

            elif msg_type == "no_tasks":
                # No tasks available, wait a bit before asking again
                await asyncio.sleep(1)

            # Wait for acknowledgment
            if msg_type != "no_tasks":
                ack = await dealer.recv_multipart()
                message_count += 1


async def main():
    # Create tasks for the task manager and workers
    tasks = [task_manager_coro()]

    # Add worker tasks
    for i in range(NUM_WORKERS):
        tasks.append(worker_coro(i))

    # Run all tasks concurrently
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Example stopped by user")