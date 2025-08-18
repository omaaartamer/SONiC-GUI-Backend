import os
import httpx
import json
from fastapi import HTTPException
from dotenv import load_dotenv
from app.models.Port import PortSummary, Port_Oper_Response
from app.redis_client import redis_client

RESTCONF_HEADERS = {
    "Accept": "application/yang-data+json"
}

load_dotenv()
SONIC_BASE_URL=os.getenv("SONIC_BASE_URL")


async def get_po_service():
    try:
        cashed = redis_client.get("port_oper")
        if cashed:
            print("Cache HIT")
            return Port_Oper_Response.model_validate(json.loads(cashed))
        
        async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
            response = await client.get(
                f"{SONIC_BASE_URL}/restconf/data/sonic-port-oper:sonic-port-oper",
                headers=RESTCONF_HEADERS
            )
            response.raise_for_status()
            redis_client.setex("port_oper", 900, json.dumps(response.json()))
            return Port_Oper_Response.model_validate(response.json())
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


async def get_port_summary_service():
    try:
        response = await get_po_service()

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
