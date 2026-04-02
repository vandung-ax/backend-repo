from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.database import get_db
from app.models.student_risk import CoVan, Khoa, Lop, TaiKhoan

router = APIRouter(prefix="/api", tags=["Admin Management"])

# Schema để nhận dữ liệu phân công từ Frontend
class AssignClassSchema(BaseModel):
    id_covan: int
    malop_list: List[str]

@router.get("/khoa-list")
def get_khoa_list(db: Session = Depends(get_db)):
    """Lấy danh sách tất cả các khoa"""
    khoas = db.query(Khoa).all()
    return [{"MaKhoa": k.MaKhoa, "TenKhoa": k.TenKhoa} for k in khoas]

@router.get("/assign-data/{ma_khoa}")
def get_assign_data(ma_khoa: str, db: Session = Depends(get_db)):
    """Lấy danh sách cố vấn và lớp thuộc một khoa cụ thể"""
    covans = db.query(CoVan).filter(CoVan.MaKhoa == ma_khoa).all()
    lops = db.query(Lop).filter(Lop.MaKhoa == ma_khoa).all()
    
    return {
        "covans": [{"Id_CoVan": c.Id_CoVan, "TenCoVan": c.TenCoVan} for c in covans],
        "lops": [{"MaLop": l.MaLop, "Id_CoVan": l.Id_CoVan} for l in lops]
    }

@router.post("/assign-lop")
def assign_lop_to_covan(data: AssignClassSchema, db: Session = Depends(get_db)):
    """Cập nhật Id_CoVan cho danh sách các lớp được chọn"""
    try:
        # Reset các lớp cũ của cố vấn này về NULL nếu bạn muốn ghi đè hoàn toàn
        # Hoặc chỉ cập nhật những lớp mới được chọn
        if data.malop_list:
            db.query(Lop).filter(Lop.MaLop.in_(data.malop_list)).update(
                {"Id_CoVan": data.id_covan}, synchronize_session=False
            )
        db.commit()
        return {"message": "Phân công lớp thành công!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))