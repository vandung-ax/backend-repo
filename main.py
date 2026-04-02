from fastapi import FastAPI
# SỬA DÒNG NÀY ĐỂ IMPORT CẢ 2:
from app.routes import authr, studentr, predict, history, covanr, adminr,advicer, accountr

app = FastAPI()

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