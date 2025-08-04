# services/SSH_Services.py

import asyncssh
import asyncio
from fastapi import WebSocket
from dotenv import load_dotenv
import os

load_dotenv()

SSH_SWITCH_IP = os.getenv("SONIC_SWITCH_IP")
SSH_USERNAME = os.getenv("SSH_USERNAME")
SSH_PASSWORD = os.getenv("SSH_PASSWORD")


class MySSHSession(asyncssh.SSHClientSession):
    def __init__(self):
        self.output_queue = asyncio.Queue()

    def data_received(self, data, datatype):
        self.output_queue.put_nowait(data)

    def connection_lost(self, exc):
        self.output_queue.put_nowait("** Connection closed **")


async def handle_ssh_session(websocket: WebSocket):
    try:
        async with asyncssh.connect(
            SSH_SWITCH_IP,
            username=SSH_USERNAME,
            password=SSH_PASSWORD
        ) as conn:
            # Create an interactive shell process with terminal support
            process = await conn.create_process(term_type='xterm')

            async def read_from_ssh():
                while True:
                    data = await process.stdout.read(1024)
                    if data:
                        await websocket.send_text(data)

            async def read_from_ws():
                while True:
                    command = await websocket.receive_text()
                    process.stdin.write(command + '\n')

            await asyncio.gather(read_from_ssh(), read_from_ws())

    except Exception as e:
        await websocket.send_text(f"Connection failed: {str(e)}")
        await websocket.close()
