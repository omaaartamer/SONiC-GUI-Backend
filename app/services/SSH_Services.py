import os
import re
import asyncssh
import asyncio
from dotenv import load_dotenv
from fastapi import WebSocket, WebSocketDisconnect
from app.models.Switch_Status import Tasks, CPU, Status


load_dotenv()

SSH_SWITCH_IP = os.getenv("SONIC_SWITCH_IP")
SSH_USERNAME = os.getenv("SSH_USERNAME")
SSH_PASSWORD = os.getenv("SSH_PASSWORD")

async def read_from_ssh(process, websocket):
    try:
        while True:
            data = await process.stdout.read(1024)
            if not data:
                try:
                    await websocket.send_text("** SSH session ended **")
                    await websocket.send_text("__RECONNECT__")  # signal frontend
                except (RuntimeError, ConnectionError):
                    pass
                break
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
            
            try:
                await websocket.close()
            except (RuntimeError, ConnectionError):
                pass


    except Exception as e:
        try:
            await websocket.send_text(f"Connection failed: {str(e)}")
        except (RuntimeError, ConnectionError):
            pass
        await websocket.close()

async def run_command(conn, command: str):
    try:
        result = await conn.run(command)
        # print (result.stdout.strip())
        return result.stdout.strip()
    except Exception as e:
        raise RuntimeError(f"SSH command failed: {str(e)}")


def parse_top_output(output: str) -> Status:
    lines = output.splitlines()
    tasks_data = {}
    cpu_data = {}

    for line in lines:
        if line.startswith("Tasks:"):
            match = re.findall(r"(\d+)\s+(\w+)", line)
            if match:
                tasks_data = {status: int(num) for num, status in match}

        elif line.startswith("%Cpu(s):"):
            match = re.findall(r"([\d\.]+)\s+(\w+)", line)
            if match:
                cpu_data = {metric: float(val) for val, metric in match}

    return Status(
        tasks=Tasks(**tasks_data),
        cpu=CPU(**cpu_data)
    )

async def switch_status(websocket: WebSocket):
    try:
        async with asyncssh.connect(
            SSH_SWITCH_IP,
            username=SSH_USERNAME,
            password=SSH_PASSWORD
        ) as conn: 
            result = await run_command(conn, "top -b -n 1")
            parsed = parse_top_output(result)
            print(parsed.model_dump())
            await websocket.send_json(parsed.model_dump())
    except Exception as e:
        await websocket.send_text(f"Error: {str(e)}")
    finally:
        await websocket.close()


