import asyncio

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

message_queue = asyncio.Queue()

async def get_message():
    while True:
        message = await asyncio.to_thread(input, 'Input your message: ')
        await message_queue.put(message)
        await asyncio.sleep(0.1)

async def send_message(writer):
    while True:
        message = await message_queue.get()
        message_queue.task_done()
        writer.write(message.encode('utf-8'))
        await writer.drain()

async def read_message(reader):
    while True:
        message = await reader.read(50)
        if message := message.decode('utf-8'):
            print()
            print(message)
        else:
            print('disconnecting from server')
            break

async def client_connection():
    try:
        server_address = ('127.0.0.52', 5200)
        reader, writer = await asyncio.open_connection(*server_address)
    except ConnectionRefusedError:
        print(f"Could not connect to specified server at {server_address}")
        return
    try:
        input_task = asyncio.create_task(get_message())
        read = asyncio.create_task(read_message(reader))
        write = asyncio.create_task(send_message(writer))
        await asyncio.gather(read, write, input_task)
    except KeyboardInterrupt:
        writer.close()
        await writer.wait_closed()

asyncio.run(client_connection())