from pydantic import BaseModel
from typing import Optional

class StudentInfoResponse(BaseModel):
    MSSV: str
    HoTen: str
    Nganh: str
    MaKhoa: str
    TenKhoa: str
    # Bạn có thể thêm các trường khác như GPA, Tín chỉ nếu DB có
    class Config:
        from_attributes = True

class StudentCreate(BaseModel):
    MSSV: str
    HoTen: str
    MaKhoa: str
    Nganh: str
    username: str
    password: str