from fastapi import APIRouter, HTTPException
from app.models.Vlan import Vlan_Post_Request, VlanWrapper 
from app.services.Delete_Vlans_Services import delete_all_vlans_from_switch, delete_vlan_by_name, delete_vlan_description_by_name
from app.services.Get_Vlans_Services import fetch_vlans
from app.services.Patch_Vlans_Services import update_vlans
from app.services.Put_Vlans_Services import update_put_vlan
from app.services.Post_Vlans_Services import add_vlans


router = APIRouter()

@router.get("/")
async def get_vlans():
    return await fetch_vlans()   


@router.post("/add_vlans")
async def add(request:Vlan_Post_Request):
    return await add_vlans(request) 



@router.put("/put_vlans")
async def put_vlan(request:VlanWrapper):
    return await update_put_vlan(request)
 


@router.patch("/patch_vlans")
async def patch_vlans(request:VlanWrapper): 
    return await update_vlans(request)


@router.delete("/delete/all", summary="Delete ALL VLAN config (VLANs + Members)")
async def delete_all_vlan_config():
    return await delete_all_vlans_from_switch()
    
@router.delete("/delete/{vlan_name}", summary="Delete a single VLAN by name")
async def delete_single_vlan(vlan_name: str):
    return await delete_vlan_by_name(vlan_name)    


@router.delete("/delete/vlan_description/{vlan_name}", summary="Delete VLAN description by name")
async def delete_vlan_description(vlan_name: str):
    return await delete_vlan_description_by_name(vlan_name)