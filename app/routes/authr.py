from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from ..models.student_risk import TaiKhoan, SinhVien, CoVan
from ..schemas.auth import LoginRequest, LoginResponse

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    # 1. Tìm tài khoản theo username
    user = db.query(TaiKhoan).filter(TaiKhoan.username == request.username).first()
    
    # 2. Kiểm tra tài khoản và mật khẩu (Dạng text thuần theo yêu cầu của bạn)
    if not user or user.password != request.password:
        raise HTTPException(status_code=401, detail="Tài khoản hoặc mật khẩu không chính xác")
    
    # 3. Lấy tên hiển thị dựa trên Role
    linked_id = None
    display_name = user.username
    if user.role == 'sinhvien' and user.sinhvien:
        display_name = user.sinhvien.HoTen
        linked_id = user.MSSV_LienKet
    elif user.role == 'covan' and user.covan:
        display_name = user.covan.TenCoVan
        linked_id = str(user.Id_CoVan_LienKet) # Lấy ID của Cố vấn
    elif user.role == 'admin':
        display_name = "Phòng Đào Tạo"

    return {
        "status": "success",
        "message": "Đăng nhập thành công",
        "id": user.id,
        "role": user.role,
        "username": user.username,
        "display_name": display_name,
        "linked_id": linked_id
    }