from fastapi import HTTPException
from dotenv import load_dotenv
from app.models.Port import PortSummary, Port_Oper_Response
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
        json_Port_data = await get_po_service()
        response = Port_Oper_Response(**json_Port_data)

        ports = [
            PortSummary(
                ifname=p.ifname,
                admin_status=p.admin_status,
                oper_status=p.oper_status,
                speed=p.speed,
                description=p.description
            ) for p in response.port.PORT_TABLE.PORT_TABLE_LIST
        ]

        return {"ports": ports}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
