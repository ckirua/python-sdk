"""
Push-Pull Example

This example demonstrates the push-pull pattern where multiple workers push messages to a single collector,
useful for distributed workloads. This is a one-way communication pattern ideal for workload distribution.
"""

import asyncio
import random
import time

from sdk.cnet import TCPSocketParameters, ZMQPull, ZMQPush

# Pull (collector) socket parameters
PULL_TCP_PARAMETERS = TCPSocketParameters(host="localhost", port=5557)

# Number of push workers to simulate
NUM_WORKERS = 5


async def pull_collector_coro():
    """Pull socket that collects messages from multiple workers"""
    print("Starting pull collector...")
    total_messages = 0
    start_time = time.time()

    async with ZMQPull(PULL_TCP_PARAMETERS) as collector:
        while True:
            # Receive message from any worker
            message = await collector.recv_multipart()
            worker_id = message[0].decode()
            data = message[1].decode()
            total_messages += 1

            elapsed = time.time() - start_time
            msg_per_sec = total_messages / elapsed if elapsed > 0 else 0

            print(
                f"Collector received from {worker_id}: {data} (Total: {total_messages}, {msg_per_sec:.1f} msg/s)"
            )


async def push_worker_coro(worker_id):
    """Push socket that sends work results to the collector"""
    worker_name = f"worker-{worker_id}"
    print(f"Starting {worker_name}...")

    async with ZMQPush(PULL_TCP_PARAMETERS) as worker:
        # Send a number of work results
        message_count = 0
        while True:
            # Simulate work being done
            work_time = random.uniform(0.1, 1.0)
            await asyncio.sleep(work_time)

            # Send result
            message_count += 1
            result = f"Result {message_count}"
            print(f"{worker_name} sending: {result}")

            # Send worker ID and result
            await worker.send_multipart([worker_name.encode(), result.encode()])


async def main():
    """Main entry point for the example"""
    # Create tasks for the collector and multiple workers
    tasks = [pull_collector_coro()]

    # Add worker tasks
    for i in range(NUM_WORKERS):
        tasks.append(push_worker_coro(i))

    # Run all tasks concurrently
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Example stopped by user")