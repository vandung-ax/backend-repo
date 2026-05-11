from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from ..models.student_risk import TaiKhoan, SinhVien, CoVan
from ..schemas.auth import LoginRequest, LoginResponse, ChangePasswordRequest
from ..utils.password import hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    # 1. Tìm tài khoản theo username
    user = db.query(TaiKhoan).filter(TaiKhoan.username == request.username).first()
    
    # 2. Kiểm tra tài khoản và mật khẩu (bcrypt hash)
    if not user or not verify_password(request.password, user.password):
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
# Import thêm ChangePasswordRequest từ schemas
@router.post("/change-password")
def change_password(request: ChangePasswordRequest, db: Session = Depends(get_db)):
    # 1. Tìm tài khoản theo username
    user = db.query(TaiKhoan).filter(TaiKhoan.username == request.username).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản")
    
    # 2. Kiểm tra mật khẩu cũ (bcrypt verify)
    if not verify_password(request.old_password, user.password):
        raise HTTPException(status_code=400, detail="Mật khẩu hiện tại không chính xác")
    
    # 3. Cập nhật mật khẩu mới (bcrypt hash)
    user.password = hash_password(request.new_password)
    db.commit()
    
    return {"status": "success", "message": "Đổi mật khẩu thành công"}
@router.get('/debug-db')
def debug_db(db: Session = Depends(get_db)):
    import os
    db_url = os.getenv('DATABASE_URL')
    user = db.query(TaiKhoan).filter(TaiKhoan.username == 'admin').first()
    return {'db_url': db_url, 'admin_hash_prefix': user.password[:10] if user and user.password else 'None'}
