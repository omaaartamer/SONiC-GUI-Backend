from fastapi import HTTPException
import httpx, os 
from dotenv import load_dotenv
from email.utils import formatdate
from app.models.Vlan import VlanWrapper 


load_dotenv()
 
SONIC_BASE_URL = os.getenv("SONIC_BASE_URL")

RESTCONF_HEADERS = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json",
}

ETH_INTERFACES = {"Ethernet0", "Ethernet1", "Ethernet2", "Ethernet3" , "Ethernet4" , "Ethernet5" , "Ethernet6"}  # till get_ethernet_interfaces is made 


async def update_vlans(request:VlanWrapper):
    
    validate_vlan_data(request)
    try:
        async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
            response = await client.patch(
                f"{SONIC_BASE_URL}/restconf/data/sonic-vlan:sonic-vlan",
                headers=RESTCONF_HEADERS,
                json=request.model_dump(by_alias=True)
            )
            response.raise_for_status()
 
            return {
                "status": response.status_code,
                "message": "VLAN configuration updated successfully.",
                "date": formatdate(timeval=None, usegmt=True)
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


    

def validate_vlan_data(request:VlanWrapper):
    try:
        vlan_list = request.wrapper.vlan.VLAN_LIST
        member_list = request.wrapper.members.VLAN_MEMBER_LIST
        
        for vlan in vlan_list:
            vlanid = vlan.vlanid
            name = vlan.name
            mac_learning = vlan.mac_learning

            if mac_learning not in {"enabled", "disabled"}:
                raise ValueError(f"Invalid mac_learning '{mac_learning}'. Must be 'enabled' or 'disabled'.")

            
            if name != f"Vlan{vlanid}":
                raise ValueError(f"VLAN name must match 'Vlan<id>' pattern (got '{name}', expected 'Vlan{vlanid}')")

            
            if not (1 <= vlanid <= 4094):
                raise ValueError(f"VLAN ID must be between 1 and 4094 (got {vlanid})")

        for member in member_list:
            ifname = member.ifname
            if ifname not in ETH_INTERFACES:
                raise ValueError(f"Invalid interface name '{ifname}'. Allowed: {', '.join(ETH_INTERFACES)}")

            if member.tagging_mode not in {"tagged", "untagged"}:
                raise ValueError(f"Invalid tagging_mode '{member.get('tagging_mode')}'. Must be 'tagged' or 'untagged'.")

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


