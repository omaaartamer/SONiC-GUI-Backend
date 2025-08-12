from fastapi import HTTPException
from dotenv import load_dotenv
from app.models.HomePortSummary import PortSummary
import httpx
import os

RESTCONF_HEADERS = {
    "Accept": "application/yang-data+json"
}


load_dotenv()

SONIC_BASE_URL=os.getenv("SONIC_BASE_URL")


async def get_po_service():
    try:
        async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
            response = await client.get(
                f"{SONIC_BASE_URL}/restconf/data/sonic-port-oper:sonic-port-oper",
                headers=RESTCONF_HEADERS
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


async def get_port_summary_service():
    try:
        async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
            response = await client.get(
                f"{SONIC_BASE_URL}/restconf/data/sonic-port-oper:sonic-port-oper",
                headers=RESTCONF_HEADERS
            )
            response.raise_for_status()
            raw_data = response.json()

            port_data = raw_data.get("sonic-port-oper:sonic-port-oper", {}).get("PORT_TABLE", {}).get("PORT_TABLE_LIST", [])

            ports = [
                PortSummary(
                    ifname=p.get("ifname", ""),
                    admin_status=p.get("admin_status", ""),
                    oper_status=p.get("oper_status", ""),
                    speed=p.get("speed", ""),
                    description=p.get("description", "")
                ) for p in port_data
            ]

            return {"ports": ports}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
