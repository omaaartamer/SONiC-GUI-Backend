from email.utils import formatdate
from fastapi import HTTPException
import httpx,os
from dotenv import load_dotenv
from app.models.Vlan import VlanWrapper

RESTCONF_HEADERS = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}


load_dotenv()
SONIC_SWITCH_IP=os.getenv("SONIC_SWITCH_IP")
SONIC_BASE_URL=os.getenv("SONIC_BASE_URL")

async def update_put_vlan(request:VlanWrapper):
    if not SONIC_BASE_URL:
        raise Exception("SONIC_BASE_URL not set in .env")

    url = f"{SONIC_BASE_URL}/restconf/data/sonic-vlan:sonic-vlan"
    
    try:
        async with httpx.AsyncClient(verify=False, timeout = 10.0) as client:
            response = await client.put(
                url,
                headers=RESTCONF_HEADERS,
                json=request.model_dump(by_alias=True)
            )
            response.raise_for_status()
            return {
                "status": response.status_code,
                "message": "VLAN configuration updated",
                "date": formatdate(timeval=None, usegmt=True)
            }
    except Exception as e: 
        raise HTTPException(status_code=500, detail=str(e))
