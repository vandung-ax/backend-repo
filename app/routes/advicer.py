from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import requests
from app.database import get_db
from app.models.student_risk import Advice

router = APIRouter(prefix="/api/advice", tags=["Advice"])

ADVICE_API_URL = "https://model-support-advice.onrender.com/predict_batch"

# Định nghĩa cấu trúc dữ liệu nhận từ Frontend
class AdvicePayload(BaseModel):
    risk_reasons: str

@router.post("/generate/{mssv}")
def generate_advice(mssv: str, req: AdvicePayload, db: Session = Depends(get_db)):
    # 1. KIỂM TRA DATABASE: Xem đã có lời khuyên cho MSSV này chưa [cite: 19-24]
    existing_advice = db.query(Advice).filter(Advice.MSSV == mssv).first()
    
    # Nếu ĐÃ CÓ: Lấy trực tiếp từ database trả về luôn, không cần gọi AI
    if existing_advice:
        return {"status": "success", "advice": existing_advice.advice_text, "source": "database"}

    # 2. NẾU CHƯA CÓ: Chuẩn bị dữ liệu gửi cho AI
    # Nếu sinh viên an toàn không có lý do rủi ro, tạo một chuỗi mặc định
    if not req.risk_reasons or not req.risk_reasons.strip():
        req.risk_reasons = "Sinh viên đang có trạng thái an toàn, điểm số và chuyên cần tốt."

    payload = [{
        "student_id": mssv,
        "risk_reasons": req.risk_reasons
    }]

    try:
        # Gọi API AI Tư vấn
        response = requests.post(ADVICE_API_URL, json=payload, timeout=60)
        if response.status_code == 200:
            ai_data = response.json()
            if ai_data and len(ai_data) > 0:
                advice_text = ai_data[0]['analysis']
                
                # 3. LƯU VÀO DATABASE: Lưu lời khuyên mới vào để lần sau dùng lại [cite: 19-24]
                new_advice = Advice(MSSV=mssv, advice_text=advice_text)
                db.add(new_advice)
                db.commit()
                
                return {"status": "success", "advice": advice_text, "source": "ai"}
            else:
                raise HTTPException(status_code=500, detail="API AI trả về rỗng.")
        else:
            raise HTTPException(status_code=response.status_code, detail="Lỗi từ API AI.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Không thể kết nối API Tư vấn: {str(e)}")