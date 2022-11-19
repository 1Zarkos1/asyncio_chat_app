import asyncio
from datetime import datetime

connected_clients = 0

async def handle_connection(reader, writer):
    client = writer.get_extra_info('peername')
    log_action('connected to', client)
    try:
        while True:
            message = await reader.read(50)
            if message := message.decode('utf-8'):
                print(f'{client} send: {message}')
            else:
                break
    except ConnectionResetError as e:
        print(f'Connection to {client} was lost')
    log_action('left', client)
    writer.close()
    await writer.wait_closed()

async def log_action(action, client):
    message = f"Client {client} {action} the server"
    if action == 'connected to':
        connected_clients += 1 
    else:
        connected_clients -= 1
    print(message)
    print(f"Members online: {connected_clients}")

async def server_work():
    server = await asyncio.start_server(handle_connection, '127.0.0.52', 5200)
    async with server:
        await server.serve_forever()

async def main():
    await server_work()

asyncio.run(server_work())
