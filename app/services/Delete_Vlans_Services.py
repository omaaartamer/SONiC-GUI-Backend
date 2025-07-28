from dotenv import load_dotenv
import os, httpx
from fastapi import HTTPException

RESTCONF_HEADERS = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}


load_dotenv()
SONIC_SWITCH_IP=os.getenv("SONIC_SWITCH_IP")
SONIC_BASE_URL=os.getenv("SONIC_BASE_URL")

AUTH = ("admin", "sonic") 

async def delete_all_vlans_from_switch():
    try:
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.delete(f"{SONIC_BASE_URL}/restconf/data/sonic-vlan:sonic-vlan", headers=RESTCONF_HEADERS, auth=AUTH, timeout=5.0)

            response.raise_for_status()

            return {"detail": "All VLANs deleted from switch successfully."}
    except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )

    
    
async def delete_vlan_by_name(vlan_name: str):
    vlan_url = f"{SONIC_BASE_URL}/restconf/data/sonic-vlan:sonic-vlan/VLAN/VLAN_LIST={vlan_name}"
    try:
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.delete(vlan_url, headers=RESTCONF_HEADERS, auth=AUTH, timeout=5.0)

            response.raise_for_status()
            return {"detail": f"VLAN '{vlan_name}' successfully deleted from the switch."}
    except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )



async def delete_vlan_description_by_name(vlan_name: str):
    url = f"{SONIC_BASE_URL}/restconf/data/sonic-vlan:sonic-vlan/VLAN/VLAN_LIST={vlan_name}/description"
    try:
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.delete(url, headers=RESTCONF_HEADERS, auth=AUTH, timeout=5.0)

            response.raise_for_status()
            return {"detail": f"VLAN '{vlan_name}' Description successfully deleted from the switch."}
    except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )

