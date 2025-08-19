import os
import re
import asyncssh
import asyncio
from dotenv import load_dotenv
from fastapi import WebSocket, WebSocketDisconnect


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
        return result.stdout.strip()
    except Exception as e:
        raise RuntimeError(f"SSH command failed: {str(e)}")


def parse_top_output(output: str):

    lines = output.splitlines()

    for line in lines:
        if line.startswith("%Cpu(s):"):
            match = re.findall(r"([\d\.]+)\s+id", line)
            if match:
                # print("in top", float(match[0]))
                return 100 - float(match[0])
                
    raise ValueError("CPU idle value not found in output")

def parse_free_output(output: str):

    lines = output.splitlines()

    for line in lines:
        if line.startswith("Mem:"):
            parts = line.split()
            total = float(parts[1][:-2])
            available = float(parts[6][:-2])
            # print(total)
            # print(available)
            mem_percentage = ((total - available)/ total) * 100
            return mem_percentage
        
    raise ValueError("Mem value not found in output")

async def switch_status(websocket: WebSocket):
    try:
        async with asyncssh.connect(
            SSH_SWITCH_IP,
            username=SSH_USERNAME,
            password=SSH_PASSWORD
        ) as conn: 
            while True:
                cpu_result = await run_command(conn, "top -b -n 1")
                cpu_usage_percentage = parse_top_output(cpu_result)
                # print("inside switch status cpu = ", cpu_used)

                memory_result = await run_command(conn, "free -h")
                mem_percentage = parse_free_output(memory_result)
                # print("inside switch status mem perc = ", mem_percentage)

                await websocket.send_json({
                    "cpu_used_percent": cpu_usage_percentage,
                    "memory_used_percent": mem_percentage
                })

                await asyncio.sleep(2)

    except Exception as e:
        await websocket.send_text(f"Error: {str(e)}")
    
    finally:
        await websocket.close()


