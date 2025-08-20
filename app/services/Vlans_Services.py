import re
import os
import httpx
import json
from fastapi import HTTPException
from dotenv import load_dotenv
from email.utils import formatdate
from app.models.Vlan import Vlan_Post_Request, VlanWrapper, SonicVLAN, SonicVLANMember, Vlan_Get_Response
from app.services.Port_Op_Services import get_po_service
from app.redis_client import redis_client

load_dotenv()
SONIC_BASE_URL = os.getenv("SONIC_BASE_URL")

RESTCONF_HEADERS = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}


async def get_Ethernet_List():
    cashed = redis_client.get("ethernet_data")
    if cashed:
        return json.loads(cashed)
    
    response = await get_po_service()
    Ethernets = []
    ports_list = response.port.PORT_TABLE.PORT_TABLE_LIST
    for port in ports_list:
        Ethernets.append(port.ifname)

    Ethernets.sort(key=lambda x: int(x.replace("Ethernet", "")))
    redis_client.setex("ethernet_data", 300, json.dumps(Ethernets))
    return Ethernets


async def check_untagged_if(eth:str):
    response = await fetch_vlans()
    if not response: # if not vlans exist so response will be empty
        return
    members_list = response.wrapper.VLAN_MEMBER.VLAN_MEMBER_LIST
    if members_list is not None:
        for i in members_list:
            if i.ifname == eth and i.tagging_mode == "untagged":
                return True
    return False


async def check_Vlan_exist(vlan:str):
    response = await fetch_vlans()
    if not response: # if not vlans exist so response will be empty
        return
    vlan_names = response.wrapper.VLAN.VLAN_LIST
    for name in vlan_names:
        if name == vlan:
            return True
    return False


async def validate_vlan_data(vlan_list:SonicVLAN, member_list: SonicVLANMember):
    
    ETH_INTERFACES = await get_Ethernet_List()
    try:
    
        for vlan in vlan_list:
            name = vlan.name
            vlanid = vlan.vlanid
            mac_learning = vlan.mac_learning


            if name != f"Vlan{vlanid}":
                raise ValueError(f"VLAN name must match 'Vlan<id>' pattern (got '{name}', expected 'Vlan{vlanid}')")

            if not (1 <= vlanid <= 4094):
                raise ValueError(f"VLAN ID must be between 1 and 4094 (got {vlanid})")
            
            if mac_learning not in {"enabled", "disabled"}:
                raise ValueError(f"Invalid mac_learning '{mac_learning}'. Must be 'enabled' or 'disabled'.")
            
        if member_list is not None:
            for member in member_list:

                member_vlan_name=member.name

                if re.fullmatch(r'Vlan\d+', member_vlan_name) is None:
                    raise ValueError("VLAN name must match 'Vlan<id>' pattern")
                
                ifname = member.ifname
                if ifname not in ETH_INTERFACES:
                    raise ValueError(f"Invalid interface name '{ifname}'. Allowed: {', '.join(ETH_INTERFACES)}")
                
                if member.tagging_mode not in {"tagged", "untagged"}:
                    raise ValueError("Invalid tagging_mode, Must be 'tagged' or 'untagged'.")
                
                if member.tagging_mode == "untagged":
                    is_untagged = await check_untagged_if(ifname)
                    if is_untagged:
                        raise ValueError(f"Interface '{ifname}' is already configured as untagged in another VLAN. Choose another interface or change the tagging mode.")
    
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    

async def fetch_vlans():
    try:
        cached_data = redis_client.get("vlans_data")
        if cached_data:
            print("Cache HIT")
            return Vlan_Get_Response.model_validate(json.loads(cached_data))
        
        async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
            response = await client.get(
                f"{SONIC_BASE_URL}/restconf/data/sonic-vlan:sonic-vlan",
                headers=RESTCONF_HEADERS,
            )

            response.raise_for_status()
            redis_client.setex("cashed_vlans", 300, json.dumps(response.json()))  # Cache for 1 hour
            return Vlan_Get_Response.model_validate(response.json())
        
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))  
    


async def post_vlans_service(request:Vlan_Post_Request):

    vlan_List= request.vlan.VLAN_LIST
    member_List= request.members.VLAN_MEMBER_LIST
    await validate_vlan_data(vlan_List, member_List)

    try:
        
        async with httpx.AsyncClient(verify=False, timeout = 10.0) as client:
            response= await client.post( f"{SONIC_BASE_URL}/restconf/data/sonic-vlan:sonic-vlan",
                                      headers=RESTCONF_HEADERS,
                                      json=request.model_dump(by_alias=True))
            
            response.raise_for_status()
            return {
                "status": response.status_code,
                "message": "VLAN added successfully",
                "date": formatdate(timeval=None, usegmt=True)
            }

        
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))  
    


async def put_vlan_service(request:VlanWrapper):
    
    vlan_List= request.wrapper.VLAN.VLAN_LIST
    member_List= request.wrapper.VLAN_MEMBER.VLAN_MEMBER_LIST
    await validate_vlan_data(vlan_List, member_List)

    try:

        async with httpx.AsyncClient(verify=False, timeout = 10.0) as client:
            response = await client.put(
                f"{SONIC_BASE_URL}/restconf/data/sonic-vlan:sonic-vlan",
                headers=RESTCONF_HEADERS,
                json=request.model_dump(by_alias=True)
            )

            response.raise_for_status()
            return {
                "status": response.status_code,
                "message": "VLAN configuration updated",
                "date": formatdate(timeval=None, usegmt=True)
            }
    
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))  


async def patch_vlans_service(request:VlanWrapper):
    
    vlan_List= request.wrapper.VLAN.VLAN_LIST
    member_List= request.wrapper.VLAN_MEMBER.VLAN_MEMBER_LIST
    await validate_vlan_data(vlan_List, member_List)

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

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))  


async def delete_all_vlans_from_switch():

    vlans = await fetch_vlans()
    if not vlans:
        raise HTTPException(status_code=404, detail="No VLANs found in the switch")
    try:
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.delete(f"{SONIC_BASE_URL}/restconf/data/sonic-vlan:sonic-vlan", headers=RESTCONF_HEADERS, timeout=10.0)

            response.raise_for_status()
            return {"detail": "All VLANs deleted from switch successfully."}

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))  

    
    
async def delete_vlan_by_name(vlan_name: str):
    vlan_url = f"{SONIC_BASE_URL}/restconf/data/sonic-vlan:sonic-vlan/VLAN/VLAN_LIST={vlan_name}"
    
    exist = await check_Vlan_exist(vlan_name)
    if not exist:
        raise HTTPException(status_code=404, detail="Vlan name not found")
    
    try:
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.delete(vlan_url, headers=RESTCONF_HEADERS,  timeout=10.0)

            response.raise_for_status()
            return {"detail": f"VLAN '{vlan_name}' successfully deleted from the switch."}
        
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))  



async def delete_vlan_description_by_name(vlan_name: str):

    url = f"{SONIC_BASE_URL}/restconf/data/sonic-vlan:sonic-vlan/VLAN/VLAN_LIST={vlan_name}/description"
    
    exist = await check_Vlan_exist(vlan_name)
    if not exist:
        raise HTTPException(status_code=404, detail="Vlan name not found")
    
    try:    
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.delete(url, headers=RESTCONF_HEADERS,  timeout=10.0)

            response.raise_for_status()
            return {"detail": f"VLAN '{vlan_name}' Description successfully deleted from the switch."}

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))  