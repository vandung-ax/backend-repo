from pydantic import BaseModel
from typing import Optional

class AdminInfoResponse(BaseModel):
    id: int
    username: str
    role: str
    display_name: str = "Quản trị viên"

# Bạn có thể thêm các Schema quản lý khác ở đây
class SystemStatsResponse(BaseModel):
    total_students: int
    total_covans: int
    total_users: int