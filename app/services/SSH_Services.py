import asyncssh
import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from dotenv import load_dotenv
import os

load_dotenv()

SSH_SWITCH_IP = os.getenv("SONIC_SWITCH_IP")
SSH_USERNAME = os.getenv("SSH_USERNAME")
SSH_PASSWORD = os.getenv("SSH_PASSWORD")

async def read_from_ssh(process, websocket):
    try:
        while True:
            data = await process.stdout.read(1024)
            if data:
                await websocket.send_text(data)
                await asyncio.sleep(0.1)
    except asyncio.CancelledError:
        pass


async def read_from_ws(process, websocket):

    try:
        while True:

            command = await websocket.receive_text()
            process.stdin.write(command + '\n')

    except WebSocketDisconnect:

        try:
            await websocket.send_text("** Client disconnected **")

        except RuntimeError: #WebSocket already closed, no need to send
            pass

        finally:
            try:
                if websocket.client_state.name != "DISCONNECTED":
                    await websocket.close()
            except RuntimeError: # If already closed during disconnect
                pass

async def handle_ssh_session(websocket: WebSocket):

    try:
        async with asyncssh.connect(
            SSH_SWITCH_IP,
            username=SSH_USERNAME,
            password=SSH_PASSWORD
        ) as conn:
            
            try:
                process = await conn.create_process(term_type='xterm')

            except Exception as e:
                await websocket.send_text(f"Failed to create SSH process: {str(e)}")
                await websocket.close()
                return
            
            # Run both readers concurrently
            read_ssh = asyncio.create_task(read_from_ssh(process, websocket))
            read_ws = asyncio.create_task(read_from_ws(process, websocket))

            pending = await asyncio.wait(
                [read_ssh, read_ws],
                return_when=asyncio.FIRST_COMPLETED
            )

            # Cancel any remaining tasks
            for task in pending:
                task.cancel()

            # Close SSH process if still open
            if not process.stdout.at_eof():
                process.stdin.write("exit\n")
                await process.wait()

    except Exception as e:
            await websocket.send_text(f"Connection failed: {str(e)}")
            await websocket.close()
