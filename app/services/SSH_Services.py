import re
import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState


ssh_sessions = {}
async def read_from_ssh(process, websocket):
    try:
        while True:
            data = await process.stdout.read(1024)
            if data:
                try:
                    await websocket.send_text(data)
                except WebSocketDisconnect:
                    break
            else:
                try:
                    await websocket.send_text("** SSH session ended **")
                    await websocket.send_text("__RECONNECT__")
                except WebSocketDisconnect:
                    break
            await asyncio.sleep(0.1)
    except asyncio.CancelledError:
        pass


async def read_from_ws(process, websocket):
    try:
        while True:
            try:
                command = await websocket.receive_text()
            except WebSocketDisconnect:
                 break

            process.stdin.write(command + '\n')

    except asyncio.CancelledError:
        pass

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

async def switch_status(websocket: WebSocket, username: str):

    await websocket.accept()
    conn = ssh_sessions.get(username)

    if not conn:
        await websocket.send_json({"error": "No active SSH session"})
        await websocket.close()
        return
    try:
            while True:
                cpu_result = await run_command(conn, "top -b -n 1")
                cpu_usage_percentage = parse_top_output(cpu_result)
                # print("inside switch status cpu = ", cpu_usage_percentage)

                memory_result = await run_command(conn, "free -h")
                mem_percentage = parse_free_output(memory_result)
                # print("inside switch status mem perc = ", mem_percentage)

                await websocket.send_json({
                    "cpu_used_percent": cpu_usage_percentage,
                    "memory_used_percent": mem_percentage
                })

                await asyncio.sleep(2)

    except WebSocketDisconnect:
        print("Client disconnected, stopping...")

    except Exception as e:
        await websocket.send_text(f"Error: {str(e)}")



async def handle_ssh_session(websocket: WebSocket, username: str):
    await websocket.accept()
    conn = ssh_sessions.get(username)

    if not conn:
        await websocket.send_json({"error": "No active SSH session"})
        await websocket.close()
        return

    try:
        process = await conn.create_process(term_type="xterm")

        read_ssh = asyncio.create_task(read_from_ssh(process, websocket))
        read_ws = asyncio.create_task(read_from_ws(process, websocket))

        done, pending = await asyncio.wait(
            [read_ssh, read_ws],
            return_when=asyncio.FIRST_COMPLETED
        )

        for task in pending:
            task.cancel()

    except Exception as e:
        if websocket.application_state == WebSocketState.CONNECTED:
            await websocket.send_json({"error": str(e)})
