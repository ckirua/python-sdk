import asyncio
import traceback

from sdk.cnet import TCPSocketParameters, ZMQPublisher, ZMQSubscriber

EXAMPLE_TCP_PARAMETERS = TCPSocketParameters(host="localhost", port=5555)


async def pub_func():
    try:
        async with ZMQPublisher(EXAMPLE_TCP_PARAMETERS) as publisher:
            count = 0
            while True:
                msg = f"msg-{count}".encode()
                print(f"PUBLISHING: topic=b'uwu', msg={msg}")
                await publisher.send_multipart([b"uwu", msg])
                count += 1
                await asyncio.sleep(1)
    except Exception as e:
        print(f"Publisher error: {e}")
        traceback.print_exc()


async def sub_func(topic: bytes, label: str):
    try:
        async with ZMQSubscriber(EXAMPLE_TCP_PARAMETERS) as subscriber:
            subscriber.subscribe(topic)
            print(f"{label} subscribed to topic: {topic!r}")
            while True:
                message = await subscriber.recv_multipart()
                print(f"{label} received: {message}")
    except Exception as e:
        print(f"{label} subscriber error: {e}")
        traceback.print_exc()


async def main():
    tasks = [
        pub_func(),
        sub_func(b"uwu", "UWU"),
        sub_func(b"awa", "AWA"),
        sub_func(b"", "ALL"),
    ]
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        print("Exiting...")


if __name__ == "__main__":
    asyncio.run(main())