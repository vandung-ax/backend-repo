from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from sqlalchemy import func
import json
from app.database import get_db
# ĐÃ THÊM IMPORT Advice
from app.models.student_risk import (
    TaiKhoan, SinhVien, RiskThresholds, RiskFeatures, 
    PredictionBatches, RiskReasons, CoVan, Lop, Advice
)

router = APIRouter(prefix="/api", tags=["History Data"])

@router.get("/data/all-results")
def get_all_results(user_id: Optional[int] = None, scope: Optional[str] = "khoa", db: Session = Depends(get_db)):
    query = db.query(
        SinhVien, RiskThresholds, RiskFeatures, PredictionBatches
    ).outerjoin(RiskThresholds, SinhVien.MSSV == RiskThresholds.MSSV)\
     .outerjoin(RiskFeatures, SinhVien.MSSV == RiskFeatures.MSSV)\
     .outerjoin(PredictionBatches, RiskThresholds.batch_id == PredictionBatches.id)

    if user_id:
        user = db.query(TaiKhoan).filter(TaiKhoan.id == user_id).first()
        if user:
            if user.role == "covan":
                covan = db.query(CoVan).filter(CoVan.Id_CoVan == user.Id_CoVan_LienKet).first()
                if covan:
                    if scope == "assigned":
                        assigned_classes = db.query(Lop.MaLop).filter(Lop.Id_CoVan == covan.Id_CoVan).all()
                        class_ids = [c[0] for c in assigned_classes]
                        if class_ids:
                            query = query.filter(SinhVien.MaLop.in_(class_ids))
                        else:
                            query = query.filter(SinhVien.MaLop == 'NONE_ASSIGNED')
                    else:
                        query = query.filter(SinhVien.MaKhoa == covan.MaKhoa)

    results = query.all()
    
    result_list = []
    for sv, threshold, features, batch in results:
        reasons_list = []
        if threshold:
            reasons = db.query(RiskReasons).filter(RiskReasons.MSSV == sv.MSSV).all()
            reasons_list = [r.reason_text for r in reasons]
            
        # LẤY LỜI KHUYÊN TỪ DATABASE
        advices = db.query(Advice).filter(Advice.MSSV == sv.MSSV).all()
        advice_list = [a.advice_text for a in advices] if advices else []
            
        result_list.append({
            "MSSV": sv.MSSV,
            "HoTen": sv.HoTen,
            "Khoa": sv.MaKhoa,
            "Lop": sv.MaLop or "Chưa xếp lớp",
            "Nganh": sv.Nganh or "Chưa xác định",
            "risk_score": threshold.risk_score if threshold else 0.0,
            "risk_level": threshold.risk_level if threshold else "AN TOÀN",
            "ai_explanation_path": threshold.ai_explanation_path if threshold else None,
            "reasons": reasons_list,
            "advices": advice_list, # <-- THÊM MẢNG LỜI KHUYÊN TRẢ VỀ CHO GIAO DIỆN
            "created_at": batch.created_at if batch else None,
            "attendance": features.Attendance if features else 0,
            "hours_studied": features.Hours_Studied if features else 0,
            "previous_scores": features.Previous_Scores if features else 0,
            "access_to_resources": features.Access_to_Resources if features else "Low",
            "motivation_level": features.Motivation_Level if features else "Low",
            "family_income": features.Family_Income if features else "Low",
            "peer_influence": features.Peer_Influence if features else "Negative",
            "distance_from_home": features.Distance_from_Home if features else "Far",
            "extracurricular_activities": features.Extracurricular_Activities if features else "No",
            "sleep_hours": features.Sleep_Hours if features else 0,
            "teacher_quality": features.Teacher_Quality if features else "Low",
        })
        
    return result_list

@router.get("/data/train-history")
def get_train_history(db: Session = Depends(get_db)):
    batches = db.query(PredictionBatches).filter(
        PredictionBatches.tree_rules_for_professor != "[]"
    ).order_by(PredictionBatches.created_at.desc()).all()
    
    result_list = []
    total_versions = len(batches) 
    
    for idx, batch in enumerate(batches):
        version_num = total_versions - idx
        try:
            tree_data = json.loads(batch.tree_rules_for_professor)
        except:
            tree_data = {}
            
        result_list.append({
            "version": version_num,
            "batch_id": batch.id,
            "created_at": batch.created_at.strftime("%d/%m/%Y %H:%M:%S") if batch.created_at else "N/A",
            "tree_rules": tree_data
        })
        
    return result_list

@router.get("/data/dashboard-stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """API đếm tổng số lượng cho trang thống kê"""
    total_sinhvien = db.query(func.count(SinhVien.MSSV)).scalar()
    total_covan = db.query(func.count(CoVan.Id_CoVan)).scalar()
    total_taikhoan = db.query(func.count(TaiKhoan.id)).scalar()
    
    return {
        "total_sinhvien": total_sinhvien,
        "total_covan": total_covan,
        "total_taikhoan": total_taikhoan
    }