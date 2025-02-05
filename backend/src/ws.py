import os, environ, asyncio, json, websockets, django
from redis import asyncio as aioredis

# Django and Environment Setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dense_review.settings')
environ.Env.read_env()
django.setup()

env = environ.Env(DEBUG=(bool, False))
WS_HOST = env('WS_HOST', default='localhost')  # Default localhost
WS_PORT = env('WS_PORT', default='8100')      # Default port 8100
REDIS_URL = env('WS_REDIS_URL')

# Track WebSocket connections by user token
USER_CONNECTIONS = {}

# WebSocket Handler
async def handler(websocket, path):
    try:
        # Authenticate User by Receiving Token
        token = await websocket.recv()
        USER_CONNECTIONS[token] = websocket
        print(f'User connected with token: {token}')

        # Keep the connection open
        await websocket.wait_closed()
    finally:
        # Remove connection on disconnect
        if token in USER_CONNECTIONS:
            USER_CONNECTIONS.pop(token)
            print(f'User disconnected with token: {token}')

# Process Celery Notifications
async def process_celery_notifications():
    # Connect to Redis
    redis = aioredis.from_url(REDIS_URL)
    pubsub = redis.pubsub()

    # Subscribe to the Celery notifications channel
    await pubsub.subscribe('celery_notifications')

    # Listen for messages
    async for message in pubsub.listen():
        if message['type'] != 'message':
            continue

        # Parse the incoming message
        data = json.loads(message['data'])
        token = data.get('token')  # User token
        msg = data.get('message') # Message content

        print(f'Notification received: {msg} for token: {token}')

        # Send message to the specific user if connected
        if token in USER_CONNECTIONS:
            websocket = USER_CONNECTIONS[token]
            try:
                await websocket.send(json.dumps(data))
                print(f'Notification sent to user with token: {token}')
            except:
                print(f'Error sending message to token: {token}')
                USER_CONNECTIONS.pop(token)  # Remove disconnected user
        else:
            print(f'No active connection for token: {token}')

# Start WebSocket Server
async def main():
    print(f'Starting WebSocket Server at {WS_HOST}:{WS_PORT}')
    async with websockets.serve(handler, WS_HOST, int(WS_PORT)):
        await process_celery_notifications()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
