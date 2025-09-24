from fastapi import APIRouter, Request, Depends
from app.core.Security import get_current_user
from app.models.Vlan import Vlan_Post_Request, VlanWrapper, Vlan_Get_Response
from app.services.Vlans_Services import fetch_vlans, post_vlans_service, patch_vlans_service, delete_all_vlans_from_switch, delete_vlan_by_name, delete_vlan_description_by_name, put_vlan_service
from app.services.Port_Op_Services import sliding_window_rate_limiter

router = APIRouter()

@router.get("/", response_model = Vlan_Get_Response)
async def get_vlans(request: Request, user: dict = Depends(get_current_user)):
    await sliding_window_rate_limiter(request, "get_vlans")
    return await fetch_vlans()   


@router.post("/add_vlans")
async def add(request:Request, body:Vlan_Post_Request, user: dict = Depends(get_current_user)):
    await sliding_window_rate_limiter(request, "add_vlan")
    return await post_vlans_service(body) 




@router.put("/put_vlans")
async def put_vlan(request:Request, body:VlanWrapper, user: dict = Depends(get_current_user)):
    await sliding_window_rate_limiter(request, "put_vlan")
    return await put_vlan_service(body)

 


@router.patch("/patch_vlans")
async def patch_vlans(body:VlanWrapper, user: dict = Depends(get_current_user)): 
    return await patch_vlans_service(body)


@router.delete("/delete/all", summary="Delete ALL VLAN config (VLANs + Members)")
async def delete_all_vlan_config( user: dict = Depends(get_current_user)):
    return await delete_all_vlans_from_switch()
    
@router.delete("/delete/{vlan_name}", summary="Delete a single VLAN by name")
async def delete_single_vlan(vlan_name: str, user: dict = Depends(get_current_user)):
    return await delete_vlan_by_name(vlan_name)    


@router.delete("/delete/vlan_description/{vlan_name}", summary="Delete VLAN description by name")
async def delete_vlan_description(vlan_name: str, user: dict = Depends(get_current_user)):
    return await delete_vlan_description_by_name(vlan_name)