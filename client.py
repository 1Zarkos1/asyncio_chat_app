import asyncio

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def client_connection():
    try:
        server_address = ('127.0.0.52', 5200)
        reader, writer = await asyncio.open_connection(*server_address)
    except ConnectionRefusedError:
        print(f"Could not connect to specified server at {server_address}")
        return
    try:
        while True:
            message = input('Input your message: ')
            writer.write(message.encode('utf-8'))
            await writer.drain()
    except KeyboardInterrupt:
        writer.close()
        await writer.wait_closed()

asyncio.run(client_connection())