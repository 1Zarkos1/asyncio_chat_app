import asyncio

connected_clients = {}

async def handle_connection(reader, writer):
    client = writer.get_extra_info('peername')
    await log_action('connected to', client, writer)
    try:
        while True:
            message = await reader.read(50)
            if message := message.decode('utf-8'):
                await distribute_message(client, message, connected_clients.values())
            else:
                break
    except ConnectionResetError as e:
        print(f'Connection to {client} was lost')
    await log_action('left', client, writer)
    writer.close()
    await writer.wait_closed()

async def log_action(action, client, writer):
    message = f"Client {client} {action} the server"
    if action == 'connected to':
        connected_clients.update({client: writer}) 
    else:
        del connected_clients[client]
    print(message)
    print(f"Members online: {len(connected_clients)}")

async def distribute_message(sender, message, receivers):
    message = f'{sender} send: {message}'
    print(message)
    for receiver in receivers:
        receiver.write(message.encode('utf-8'))
        await receiver.drain()

async def server_work():
    server = await asyncio.start_server(handle_connection, '127.0.0.52', 5200)
    async with server:
        await server.serve_forever()

asyncio.run(server_work())
