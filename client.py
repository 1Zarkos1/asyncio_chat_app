import asyncio
from queue import Queue

from tk_app import gui, AppClosedException
from server import DEFAULT_SERVER_ADDRESS

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

message_queue = asyncio.Queue()
gui_inbox = Queue()
gui_outqueue = Queue()

async def get_message_from_gui():
    while True:
        message = await asyncio.to_thread(gui_outqueue.get)
        await message_queue.put(message)
        await asyncio.sleep(0.1)

async def send_message(writer):
    while True:
        message = await message_queue.get()
        message_queue.task_done()
        writer.write(message.encode('utf-8'))
        await writer.drain()

async def receive_message(reader):
    while True:
        message = await reader.read(50)
        if message := message.decode('utf-8'):
            gui_inbox.put(message)
        else:
            print('disconnecting from server')
            break

async def client_connection():
    try:
        reader, writer = await asyncio.open_connection(*DEFAULT_SERVER_ADDRESS)
    except ConnectionRefusedError:
        print(f"Could not connect to specified server at {server_address}")
        return
    try:
        message_from_gui = asyncio.create_task(get_message_from_gui())
        receive = asyncio.create_task(receive_message(reader))
        send = asyncio.create_task(send_message(writer))
        gui_app = asyncio.to_thread(gui, gui_inbox, gui_outqueue)
        await asyncio.gather(message_from_gui, receive, send, gui_app)
    except (AppClosedException, KeyboardInterrupt):
        print("closing connections")
        writer.close()
        await writer.wait_closed()

asyncio.run(client_connection())