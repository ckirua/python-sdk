"""
Dealer-Router Example

This example demonstrates the dealer-router pattern where multiple dealers connect to a single router,
enabling many-to-one messaging. The router can identify which dealer sent each message and route
responses back to the correct dealer.
"""

import asyncio

from sdk.cnet import TCPSocketParameters, ZMQDealer, ZMQRouter

# Router (server) socket parameters
ROUTER_TCP_PARAMETERS = TCPSocketParameters(host="localhost", port=5556)

# Number of dealer clients to simulate
NUM_DEALERS = 5


async def router_coro():
    """Router socket that receives messages from multiple dealers"""
    print("Starting router (server)...")
    async with ZMQRouter(ROUTER_TCP_PARAMETERS) as router:
        while True:
            # Router receives [identity, empty, message]
            message = await router.recv_multipart()
            dealer_id = message[0]
            content = message[2]
            print(f"Router received from {dealer_id.hex()[:8]}: {content.decode()}")

            # Send reply back to the specific dealer
            await router.send_multipart(
                [dealer_id, b"", f"Received: {content.decode()}".encode()]
            )


async def dealer_coro(dealer_id):
    """Dealer socket that sends messages to the router"""
    # Create a unique dealer ID for tracking
    dealer_name = f"dealer-{dealer_id}"
    dealer_id_bytes = dealer_name.encode()

    print(f"Starting {dealer_name}...")
    async with ZMQDealer(ROUTER_TCP_PARAMETERS) as dealer:
        # Send 5 messages with a delay between them
        for i in range(5):
            message = f"Message {i+1} from {dealer_name}"
            print(f"{dealer_name} sending: {message}")

            # Dealer sends [empty, message]
            await dealer.send_multipart([b"", message.encode()])

            # Receive reply from router
            reply = await dealer.recv_multipart()
            print(f"{dealer_name} received: {reply[1].decode()}")

            # Random delay between 0.5 and 2 seconds
            await asyncio.sleep(0.5 + (dealer_id * 0.3))


async def main():
    """Main entry point for the example"""
    # Create tasks for the router and multiple dealers
    tasks = [router_coro()]

    # Add dealer tasks
    for i in range(NUM_DEALERS):
        tasks.append(dealer_coro(i))

    # Run all tasks concurrently
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Example stopped by user")