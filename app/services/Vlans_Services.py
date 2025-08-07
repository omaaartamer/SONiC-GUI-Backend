import re
import os
import httpx
from fastapi import HTTPException
from dotenv import load_dotenv
from email.utils import formatdate
from app.models.Vlan import Vlan_Post_Request, VlanWrapper, SonicVLAN, SonicVLANMember, Vlan_Get_Response
from app.services.Port_Op_Services import get_po_service
from app.models.Port import Port_Oper_Response

load_dotenv()
 
SONIC_BASE_URL = os.getenv("SONIC_BASE_URL")


RESTCONF_HEADERS = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}



async def get_Ethernet_List():
    json_Port_data = await get_po_service()
    response = Port_Oper_Response(**json_Port_data)
    Ethernets = []
    ports_list = response.port.PORT_TABLE.PORT_TABLE_LIST
    for port in ports_list:
        Ethernets.append(port.ifname)

    Ethernets.sort(key=lambda x: int(x.replace("Ethernet", "")))
    # print("Ethernets: ", (Ethernets))
    return Ethernets


async def check_untagged_if(eth:str):

    json_Vlan_data = await fetch_vlans()
    response = Vlan_Get_Response(**json_Vlan_data)
    members_list = response.wrapper.VLAN_MEMBER.VLAN_MEMBER_LIST
    if members_list is not None:
        for i in members_list:
            if i.ifname == eth and i.tagging_mode == "untagged":
                return True
    return False



async def validate_vlan_data(vlan_list:SonicVLAN, member_list: SonicVLANMember):
    
    ETH_INTERFACES= await get_Ethernet_List()
    # print(ETH_INTERFACES)
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
        async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
            response = await client.get(
                f"{SONIC_BASE_URL}/restconf/data/sonic-vlan:sonic-vlan",
                headers=RESTCONF_HEADERS,
            )

            response.raise_for_status()
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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

        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


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
    except Exception as e: 
        raise HTTPException(status_code=500, detail=str(e))


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

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def delete_all_vlans_from_switch():
    try:
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.delete(f"{SONIC_BASE_URL}/restconf/data/sonic-vlan:sonic-vlan", headers=RESTCONF_HEADERS, timeout=10.0)

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
            response = await client.delete(vlan_url, headers=RESTCONF_HEADERS,  timeout=10.0)

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
            response = await client.delete(url, headers=RESTCONF_HEADERS,  timeout=10.0)

            response.raise_for_status()
            return {"detail": f"VLAN '{vlan_name}' Description successfully deleted from the switch."}
    except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )