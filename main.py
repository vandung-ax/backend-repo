from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # BƯỚC 1: Thêm dòng import này

# SỬA DÒNG NÀY ĐỂ IMPORT CẢ 2:
from app.routes import authr, studentr, predict, history, covanr, adminr, advicer, accountr
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import Depends
from app.database import get_db


app = FastAPI()

# BƯỚC 2: THÊM TOÀN BỘ ĐOẠN NÀY ĐỂ MỞ CỬA CHO REACT (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép mọi frontend (bao gồm cổng 5173 của React) gọi API
    allow_credentials=True,
    allow_methods=["*"],  # Cho phép tất cả các phương thức GET, POST, PUT, DELETE
    allow_headers=["*"],
)

# ĐĂNG KÝ CÁC ROUTER TẠI ĐÂY:
app.include_router(authr.router)
app.include_router(adminr.router)
app.include_router(predict.router)
app.include_router(history.router)
app.include_router(studentr.router)
app.include_router(covanr.router)
app.include_router(advicer.router)
app.include_router(accountr.router)

@app.get("/")
def root():
    return {"message": "Backend đang chạy ổn định!"}

@app.get("/healthcheck")
def healthcheck(db: Session = Depends(get_db)):
    try:
        # Thực hiện một truy vấn SQL cực nhẹ để giữ Aiven không bị tắt
        db.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "message": "Hệ thống và Database đang hoạt động!",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": "Không thể kết nối Database",
            "error": str(e)
        }