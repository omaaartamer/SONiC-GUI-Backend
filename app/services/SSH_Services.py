import asyncssh
import asyncio
from fastapi import WebSocket, WebSocketDisconnect
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
            process = await conn.create_process(term_type='xterm')

            async def read_from_ssh():
                try:
                    while True:
                        data = await process.stdout.read(1024)
                        if data:
                            await websocket.send_text(data)
                        await asyncio.sleep(0.1)
                except asyncio.CancelledError:
                    pass

            async def read_from_ws():
                try:
                    while True:
                        command = await websocket.receive_text()
                        process.stdin.write(command + '\n')
                except WebSocketDisconnect:
                     try:
                         await websocket.send_text("** Client disconnected **")
                     except RuntimeError:
        # WebSocket already closed, no need to send
                         pass
                finally:
                    try:
                        if websocket.client_state.name != "DISCONNECTED":
                             await websocket.close()
                    except RuntimeError:
            # If already closed during disconnect
                         pass


            # Run both readers concurrently
            read_ssh = asyncio.create_task(read_from_ssh())
            read_ws = asyncio.create_task(read_from_ws())

            done, pending = await asyncio.wait(
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
        try:
            await websocket.send_text(f"Connection failed: {str(e)}")
        except Exception:
            pass
        await websocket.close()
