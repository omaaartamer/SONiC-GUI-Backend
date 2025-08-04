import asyncio
import websockets

async def test_ssh_websocket():
    uri = "ws://localhost:8000/ws/ssh"
    print("Starting WebSocket client...")

    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to WebSocket SSH session!")

            async def send_commands():
                while True:
                    cmd = await asyncio.get_event_loop().run_in_executor(None, input, ">>> ")
                    await websocket.send(cmd)

            async def receive_output():
                while True:
                    response = await websocket.recv()
                    print(response)

            await asyncio.gather(send_commands(), receive_output())

    except Exception as e:
        print("Connection failed:", str(e))

asyncio.run(test_ssh_websocket())
