from pydantic import BaseModel
from typing import Optional

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    status: str
    message: str
    id: Optional[int] = None
    role: Optional[str] = None
    username: Optional[str] = None
    display_name: Optional[str] = None # Tên hiển thị (Tên SV hoặc Tên Cố vấn)
    linked_id: Optional[str] = None # Thêm trường này để lưu ID liên kết

class ChangePasswordRequest(BaseModel):
    username: str
    old_password: str
    new_password: str