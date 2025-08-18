from fastapi import APIRouter
from app.models.Port import PortSummaryList, Port_Oper_Response
from app.services.Port_Op_Services import get_po_service, get_port_summary_service


router = APIRouter()



@router.get("/", response_model=Port_Oper_Response)
async def get_port_oper():
    return await get_po_service()

@router.get("/status-summary", response_model=PortSummaryList)
async def get_port_summary():
    return await get_port_summary_service()