from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models.student_risk import TaiKhoan

router = APIRouter(prefix="/api/account", tags=["Account Management"])

# --- SCHEMAS (Định nghĩa dữ liệu đầu vào từ Frontend) ---
class AccountBase(BaseModel):
    role: str
    MSSV_LienKet: Optional[str] = None
    Id_CoVan_LienKet: Optional[int] = None

class AccountCreate(AccountBase):
    username: str
    password: str

class AccountUpdate(AccountBase):
    password: Optional[str] = None # Cho phép null nếu người dùng không muốn đổi mật khẩu

# --- ROUTES ---

# 1. Lấy tất cả tài khoản
@router.get("/all")
def get_all_accounts(db: Session = Depends(get_db)):
    accounts = db.query(TaiKhoan).all()
    return accounts

# 2. Thêm tài khoản mới
@router.post("/add")
def add_account(acc: AccountCreate, db: Session = Depends(get_db)):
    # Kiểm tra xem username đã tồn tại chưa
    existing_acc = db.query(TaiKhoan).filter(TaiKhoan.username == acc.username).first()
    if existing_acc:
        raise HTTPException(status_code=400, detail="Tên đăng nhập đã tồn tại trong hệ thống")
    
    new_acc = TaiKhoan(
        username=acc.username,
        password=acc.password, 
        role=acc.role,
        MSSV_LienKet=acc.MSSV_LienKet,
        Id_CoVan_LienKet=acc.Id_CoVan_LienKet
    )
    db.add(new_acc)
    try:
        db.commit()
        db.refresh(new_acc)
        return {"status": "success", "message": "Thêm tài khoản thành công", "id": new_acc.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi database: {str(e)}")

# 3. Cập nhật tài khoản
@router.put("/update/{account_id}")
def update_account(account_id: int, acc: AccountUpdate, db: Session = Depends(get_db)):
    db_acc = db.query(TaiKhoan).filter(TaiKhoan.id == account_id).first()
    if not db_acc:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản")
    
    # Cập nhật thông tin
    db_acc.role = acc.role
    db_acc.MSSV_LienKet = acc.MSSV_LienKet
    db_acc.Id_CoVan_LienKet = acc.Id_CoVan_LienKet
    
    # Chỉ cập nhật mật khẩu nếu có gửi lên (chuỗi không rỗng)
    if acc.password: 
        db_acc.password = acc.password
        
    try:
        db.commit()
        return {"status": "success", "message": "Cập nhật tài khoản thành công"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi database: {str(e)}")

# 4. Xóa tài khoản
@router.delete("/delete/{account_id}")
def delete_account(account_id: int, db: Session = Depends(get_db)):
    db_acc = db.query(TaiKhoan).filter(TaiKhoan.id == account_id).first()
    if not db_acc:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản")
    
    db.delete(db_acc)
    try:
        db.commit()
        return {"status": "success", "message": "Xóa tài khoản thành công"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi database: {str(e)}")