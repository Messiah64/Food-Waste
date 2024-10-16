import asyncio
import websockets

async def handle_client(websocket, path):
    try:
        print(f"New client connected: {websocket.remote_address}")
        async for message in websocket:
            print(f"Received NFC data: {message}")
    except websockets.exceptions.ConnectionClosed:
        print(f"Client disconnected: {websocket.remote_address}")

async def main():
    server = await websockets.serve(handle_client, "0.0.0.0", 8765)
    print("WebSocket server started on port 8765")
    print("Waiting for NFC data...")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())