from pydantic import BaseModel, Field
from typing import List, Optional

class Port_Oper(BaseModel):
    admin_status: str
    alias: str
    description: str
    ifname: str
    index: int
    lanes: str
    mtu: int
    oper_status: str
    speed: str

class Port_Oper_Table_List(BaseModel):
    PORT_TABLE_LIST: List[Port_Oper]

class Port_Oper_Table(BaseModel):
    PORT_TABLE: Port_Oper_Table_List
    
class Port_Oper_Response(BaseModel):
    port: Port_Oper_Table = Field(..., alias="sonic-port-oper:sonic-port-oper")


class PortSummary(BaseModel):
    ifname: str
    admin_status: str
    oper_status: str
    speed: str
    description: Optional[str]

class PortSummaryList(BaseModel):
    ports: List[PortSummary]