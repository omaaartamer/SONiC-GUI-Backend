import os
from fastapi import APIRouter
from dotenv import load_dotenv
from app.services.Get_Port_Op_Services import get_po_service


router = APIRouter()

load_dotenv()
SONIC_SWITCH_IP=os.getenv("SONIC_SWITCH_IP")


@router.get("/po")
async def get_port_oper():
    return await get_po_service()