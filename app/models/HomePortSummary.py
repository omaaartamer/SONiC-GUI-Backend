from pydantic import BaseModel
from typing import List, Optional

class PortSummary(BaseModel):
    ifname: str
    admin_status: str
    oper_status: str
    speed: str
    description: Optional[str]

class PortSummaryList(BaseModel):
    ports: List[PortSummary]
