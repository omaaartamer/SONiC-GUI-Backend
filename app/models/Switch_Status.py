from pydantic import BaseModel


class Tasks(BaseModel):
    total: int
    running: int
    sleeping: int
    stopped: int
    zombie: int

class CPU(BaseModel):
    us: float  # user space
    sy: float  # system
    ni: float  # nice
    id: float  # idle
    wa: float  # wait
    hi: float  # hardware interrupts
    si: float  # software interrupts
    st: float  # stolen time

class Status(BaseModel):
    tasks: Tasks
    cpu: CPU