from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from typing import List
from ..schemas.covan import CoVanInfoResponse
from ..models.student_risk import CoVan, Khoa

router = APIRouter(prefix="/api/covan", tags=["CoVan"])

@router.get("/all", response_model=List[CoVanInfoResponse])
def get_all_covans(db: Session = Depends(get_db)):
    covans = db.query(CoVan).all()
    return [{
        "Id_CoVan": c.Id_CoVan,
        "TenCoVan": c.TenCoVan,
        "MaKhoa": c.MaKhoa,
        "TenKhoa": c.khoa.TenKhoa if c.khoa else "Chưa xác định"
    } for c in covans]

# --- BỔ SUNG CÁC HÀM DƯỚI ĐÂY ---

@router.post("/add")
def add_advisor(data: dict, db: Session = Depends(get_db)):
    # data nhận từ payload: {"TenCoVan": "...", "MaKhoa": "..."}
    new_covan = CoVan(TenCoVan=data['TenCoVan'], MaKhoa=data['MaKhoa'])
    db.add(new_covan)
    db.commit()
    return {"status": "success"}

@router.put("/update/{advisor_id}")
def update_advisor(advisor_id: int, data: dict, db: Session = Depends(get_db)):
    covan = db.query(CoVan).filter(CoVan.Id_CoVan == advisor_id).first()
    if not covan: raise HTTPException(status_code=404)
    covan.TenCoVan = data['TenCoVan']
    covan.MaKhoa = data['MaKhoa']
    db.commit()
    return {"status": "success"}

@router.delete("/delete/{advisor_id}")
def delete_advisor(advisor_id: int, db: Session = Depends(get_db)):
    db.query(CoVan).filter(CoVan.Id_CoVan == advisor_id).delete()
    db.commit()
    return {"status": "success"}