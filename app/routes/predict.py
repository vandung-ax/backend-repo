from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import pandas as pd
import io
import requests
import json
from typing import Optional
from app.database import get_db
from app.models.student_risk import (
    SinhVien, Khoa, Lop, RiskFeatures, RiskThresholds, RiskReasons, PredictionBatches, TaiKhoan
)

router = APIRouter(prefix="/api", tags=["Prediction & Retrain"])

AI_API_URL = "https://ai-student-api.onrender.com/api/predict_batch"
AI_RETRAIN_URL = "https://ai-student-api.onrender.com/api/retrain_end_of_semester"
AI_CURRENT_TREE_URL = "https://ai-student-api.onrender.com/api/model/current_tree" # <-- THÊM DÒNG NÀY

@router.post("/upload-predict")
async def upload_and_predict(
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...), 
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Chỉ chấp nhận file .csv")

    content = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(content), encoding='utf-8-sig')
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Không thể đọc file CSV: {str(e)}")

    feature_columns = [
        "Attendance", "Hours_Studied", "Previous_Scores", "Access_to_Resources",
        "Motivation_Level", "Family_Income", "Peer_Influence", "Distance_from_Home",
        "Extracurricular_Activities", "Sleep_Hours", "Teacher_Quality"
    ]
    
    missing_cols = [c for c in feature_columns if c not in df.columns]
    if missing_cols:
        raise HTTPException(status_code=400, detail=f"File thiếu các cột: {missing_cols}")

    records_to_send = df[feature_columns].to_dict(orient="records")

    try:
        response = requests.post(AI_API_URL, json=records_to_send, timeout=60)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Lỗi phản hồi từ API Dự báo AI")
        ai_data = response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Không thể kết nối API Dự báo: {str(e)}")

    try:
        # CHỈ DỰ BÁO: Cây ép thành "[]"
        new_batch = PredictionBatches(
            tree_rules_for_professor="[]", 
            uploaded_by=user_id  
        )
        db.add(new_batch)
        db.flush() 

        for idx, row in df.iterrows():
            mssv = str(row['MSSV'])
            
            ten_khoa = str(row['Khoa'])
            khoa = db.query(Khoa).filter(Khoa.TenKhoa == ten_khoa).first()
            if not khoa:
                khoa = Khoa(MaKhoa=ten_khoa[:20], TenKhoa=ten_khoa)
                db.add(khoa)
                db.flush()
                
            ma_lop_csv = row.get('Lớp')
            lop_db = None
            if pd.notna(ma_lop_csv) and str(ma_lop_csv).strip() != "":
                ma_lop_str = str(ma_lop_csv).strip()
                lop_db = db.query(Lop).filter(Lop.MaLop == ma_lop_str).first()
                if not lop_db:
                    lop_db = Lop(MaLop=ma_lop_str[:20], TenLop=ma_lop_str, MaKhoa=khoa.MaKhoa)
                    db.add(lop_db)
                    db.flush()    

            sinhvien = db.query(SinhVien).filter(SinhVien.MSSV == mssv).first()
            if not sinhvien:
                sinhvien = SinhVien(
                    MSSV=mssv,
                    HoTen=row['Họ Tên'],
                    MaKhoa=khoa.MaKhoa,
                    Nganh=row['Ngành'],
                    MaLop=lop_db.MaLop if lop_db else None
                )
                db.add(sinhvien)
                db.flush() 
            
            new_features = RiskFeatures(
                MSSV=mssv,
                Attendance=row['Attendance'],
                Hours_Studied=row['Hours_Studied'],
                Previous_Scores=row['Previous_Scores'],
                Access_to_Resources=row['Access_to_Resources'],
                Motivation_Level=row['Motivation_Level'],
                Family_Income=row['Family_Income'],
                Peer_Influence=row['Peer_Influence'],
                Distance_from_Home=row['Distance_from_Home'], 
                Extracurricular_Activities=row['Extracurricular_Activities'],
                Sleep_Hours=row['Sleep_Hours'],
                Teacher_Quality=row['Teacher_Quality']
            )
            db.add(new_features)

            res = ai_data['results'][idx]
            new_threshold = RiskThresholds(
                MSSV=mssv,
                risk_score=res['risk_score_percent'] / 100,
                risk_level=res['risk_level'],
                ai_explanation_path=json.dumps(res['ai_explanation_path']),
                batch_id=new_batch.id
            )
            db.add(new_threshold)

            reasons = res.get('sorted_reasons_for_ui', [])
            for reason_text in reasons:
                db.add(RiskReasons(MSSV=mssv, reason_text=reason_text))

        db.commit()
        return {"message": "Dự báo thành công và đã lưu vào cơ sở dữ liệu!"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi lưu trữ Database: {str(e)}")

# --- BƯỚC 1: Đẩy file đi ---
@router.post("/retrain-model")
async def retrain_model(
    file: UploadFile = File(...), 
    user_id: Optional[int] = None
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Chỉ chấp nhận file .csv")

    content = await file.read()
    
    try:
        files = {"file": (file.filename, content, "text/csv")}
        response = requests.post(AI_RETRAIN_URL, files=files, timeout=60)
        
        if response.status_code == 200:
            result_ai = response.json()
            # KHÔNG LƯU DB Ở ĐÂY NỮA, CHỈ TRẢ KẾT QUẢ VỀ
            return result_ai
        else:
            error_msg = response.text
            raise HTTPException(status_code=response.status_code, detail=f"Lỗi từ máy chủ AI: {error_msg}")
            
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Lỗi kết nối hoặc lưu trữ: {str(e)}")

# --- BƯỚC 2: Kéo cây về ---
@router.post("/sync-latest-tree")
def sync_latest_tree(user_id: Optional[int] = None, db: Session = Depends(get_db)):
    try:
        response = requests.get(AI_CURRENT_TREE_URL, timeout=30)
        
        if response.status_code == 200:
            tree_data = response.json()
            
            # LƯU CÂY VÀO DATABASE
            new_train_batch = PredictionBatches(
                tree_rules_for_professor=json.dumps(tree_data), 
                uploaded_by=user_id
            )
            db.add(new_train_batch)
            db.commit()
            
            return {"message": "Đã đồng bộ thành công cây quyết định mới nhất từ AI!"}
        else:
            raise HTTPException(status_code=500, detail="Máy chủ AI chưa sẵn sàng hoặc lỗi.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi đồng bộ: {str(e)}")