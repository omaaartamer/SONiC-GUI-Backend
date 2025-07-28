from typing import List, Literal, Optional
from pydantic import BaseModel, Field, model_validator

class Vlan(BaseModel):
    name: str
    vlanid: int
    description: Optional[str]
    mac_learning: Literal["enabled", "disabled"]

class Vlan_memberList(BaseModel):
    name: str
    ifname: str
    tagging_mode: Literal["untagged", "tagged"]

class SonicVLAN(BaseModel):
    VLAN_LIST: List[Vlan]

class SonicVLANMember(BaseModel):
    VLAN_MEMBER_LIST: Optional[List[Vlan_memberList]]=None


class Vlan_Post_Request(BaseModel):
    vlan: SonicVLAN = Field(..., alias="sonic-vlan:VLAN")
    members: Optional[SonicVLANMember] = Field(None, alias="sonic-vlan:VLAN_MEMBER")

    @model_validator(mode = 'before')
    def check_vlans_members(cls, values):
        vlan_data = values.get("sonic-vlan:VLAN")
        if not vlan_data or not vlan_data.get("VLAN_LIST"):
            raise ValueError("sonic-vlan:VLAN with VLAN_LIST is required")
        return values


class Vlan_Put_Request(BaseModel):  # This is the nested content inside "sonic-vlan:sonic-vlan"
    vlan: SonicVLAN = Field(..., alias="VLAN")
    members: Optional[SonicVLANMember] = Field(None, alias="VLAN_MEMBER")

    @model_validator(mode="before")
    def check_vlans_members(cls, values):
        vlan_data = values.get("VLAN")
        if not vlan_data or not vlan_data.get("VLAN_LIST"):
            raise ValueError("VLAN with VLAN_LIST is required")
        return values
class Put_VlanWrapper(BaseModel):
    request: Vlan_Put_Request = Field(..., alias="sonic-vlan:sonic-vlan")