from fastapi import APIRouter, HTTPException
from app.services.sonic_services import fetch_vlans


router = APIRouter()


@router.get("/")
async def get_vlans():
 return await fetch_vlans()   

