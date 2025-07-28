from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.Auth_Router import router as auth_router
from app.routers.Vlans_Router import router as vlans_router
from app.routers.Port_Oper_Router import router as port_op_router

app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)


app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(vlans_router, prefix="/vlans",tags=["Vlans"])
app.include_router(port_op_router, prefix="/portOp",tags=["Port Operation"])
