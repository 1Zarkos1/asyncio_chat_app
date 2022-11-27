import asyncio
from queue import Queue

from tk_app import gui, AppClosedException
from server import DEFAULT_SERVER_ADDRESS

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

message_queue = asyncio.Queue()
gui_inbox = Queue()
gui_outqueue = Queue()

run_flag = 1
exit_obj = object()

async def get_message_from_gui():
    while run_flag:
        message = await asyncio.to_thread(gui_outqueue.get)
        if message != exit_obj:
            await message_queue.put(message)
            await asyncio.sleep(0.1)

async def send_message(writer):
    while run_flag:
        message = await message_queue.get()
        message_queue.task_done()
        writer.write(message.encode('utf-8'))
        await writer.drain()

async def receive_message(reader):
    while run_flag:
        message = await reader.read(50)
        print(message)
        if message := message.decode('utf-8'):
            gui_inbox.put(message)
        else:
            print('disconnecting from server')
            break

async def shut_down(tasks, writer):
    global run_flag
    run_flag = 0

    gui_outqueue.put(exit_obj)

    for task in tasks:
        try:
            task.cancel()
            await task
        except asyncio.CancelledError:
            print("...")

    writer.close()
    await writer.wait_closed()

async def client_connection():
    try:
        reader, writer = await asyncio.open_connection(*DEFAULT_SERVER_ADDRESS)
    except ConnectionRefusedError:
        print(f"Could not connect to specified server at {server_address}")
        return
    try:
        coros = [get_message_from_gui(), receive_message(reader), send_message(writer)]
        background_tasks = [asyncio.create_task(coro) for coro in coros]
        gui_app = asyncio.to_thread(gui, gui_inbox, gui_outqueue)
        await gui_app
    except KeyboardInterrupt:
        print("keyboard interruption")
    await shut_down(backgroun_tasks, writer)

asyncio.run(client_connection())