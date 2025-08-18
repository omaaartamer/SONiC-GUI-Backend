from fastapi import APIRouter, Request
from app.models.Vlan import Vlan_Post_Request, VlanWrapper, Vlan_Get_Response
from app.services.Vlans_Services import fetch_vlans, post_vlans_service, patch_vlans_service, delete_all_vlans_from_switch, delete_vlan_by_name, delete_vlan_description_by_name, put_vlan_service
from app.services.Port_Op_Services import sliding_window_rate_limiter

router = APIRouter()

@router.get("/", response_model = Vlan_Get_Response)
async def get_vlans(request: Request):
    await sliding_window_rate_limiter(request)
    return await fetch_vlans()   


@router.post("/add_vlans")
async def add(request:Vlan_Post_Request):
    await sliding_window_rate_limiter(request)
    return await post_vlans_service(request) 




@router.put("/put_vlans")
async def put_vlan(request:VlanWrapper):
    await sliding_window_rate_limiter(request)
    return await put_vlan_service(request)

 


@router.patch("/patch_vlans")
async def patch_vlans(request:VlanWrapper): 
    await sliding_window_rate_limiter(request)
    return await patch_vlans_service(request)


@router.delete("/delete/all", summary="Delete ALL VLAN config (VLANs + Members)")
async def delete_all_vlan_config():
    return await delete_all_vlans_from_switch()
    
@router.delete("/delete/{vlan_name}", summary="Delete a single VLAN by name")
async def delete_single_vlan(vlan_name: str):
    return await delete_vlan_by_name(vlan_name)    


@router.delete("/delete/vlan_description/{vlan_name}", summary="Delete VLAN description by name")
async def delete_vlan_description(vlan_name: str):
    return await delete_vlan_description_by_name(vlan_name)