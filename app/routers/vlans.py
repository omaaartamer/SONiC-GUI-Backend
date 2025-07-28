from fastapi import APIRouter, HTTPException
from app.services.DeleteServices import delete_all_vlans_from_switch, delete_vlan_by_name, delete_vlan_description_by_name
from app.services.Get_Vlans_services import fetch_vlans
from app.models.vlan import Vlan_request
from app.services.Put_Vlans_services import update_put_vlan
from app.services.Post_Vlans_services import add_vlans
router = APIRouter()



@router.get("/")
async def get_vlans():
    return await fetch_vlans()   


@router.post("/add_vlans")
async def add(request:Vlan_request):
    return await add_vlans(request) 



@router.put("/put_vlans", tags=["vlans"])
async def put_vlan(payload: Vlan_request):
    try:
        # Restructure it to match the switch's expected payload
        formatted_payload = {
            "sonic-vlan:sonic-vlan": {
                "VLAN": payload.vlan.dict(by_alias=True),
                "VLAN_MEMBER": payload.members.dict(by_alias=True)
            }
        }
        return await update_put_vlan(formatted_payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/delete/all-vlan-config", summary="Delete ALL VLAN config (VLANs + Members)")
async def delete_all_vlan_config():
    try:
        return await delete_all_vlans_from_switch()
    except HTTPException as http_exc:
        raise http_exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {exc}")
    
@router.delete("/delete/vlan/{vlan_name}", summary="Delete a single VLAN by name")
async def delete_single_vlan(vlan_name: str):
    return await delete_vlan_by_name(vlan_name)    


@router.delete(
    "/delete/vlan-description/{vlan_name}", summary="Delete VLAN description by name"
)
async def delete_vlan_description(vlan_name: str):
    return await delete_vlan_description_by_name(vlan_name)    