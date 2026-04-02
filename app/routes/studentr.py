# app/routes/studentr.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
# Import đầy đủ các bảng có liên quan đến MSSV
from ..models.student_risk import SinhVien, Khoa, TaiKhoan, RiskFeatures, RiskThresholds, RiskReasons, Advice
from ..schemas.student import StudentInfoResponse, StudentCreate

router = APIRouter(prefix="/api/student", tags=["Student"])

@router.get("/all", response_model=List[StudentInfoResponse])
def get_all_students(db: Session = Depends(get_db)):
    # Bỏ qua các dòng lỗi NULL (nếu có)
    students = db.query(SinhVien).filter(SinhVien.MSSV.isnot(None)).all()
    return [{
        "MSSV": s.MSSV,
        "HoTen": s.HoTen if s.HoTen else "Chưa có tên",
        "MaKhoa": s.MaKhoa if s.MaKhoa else "Chưa xác định",
        "TenKhoa": s.khoa.TenKhoa if s.khoa else "Chưa xác định",
        "Nganh": s.Nganh if s.Nganh else "Chưa xác định"
    } for s in students]

@router.post("/add")
def add_student(data: StudentCreate, db: Session = Depends(get_db)):
    # 1. Kiểm tra trùng MSSV
    if db.query(SinhVien).filter(SinhVien.MSSV == data.MSSV).first():
        raise HTTPException(status_code=400, detail="MSSV đã tồn tại trong hệ thống")

    # 2. Thêm Sinh viên
    new_sv = SinhVien(MSSV=data.MSSV, HoTen=data.HoTen, MaKhoa=data.MaKhoa, Nganh=data.Nganh)
    db.add(new_sv)
    db.flush()

    # 3. Tạo Tài khoản liên kết
    new_acc = TaiKhoan(username=data.username, password=data.password, role="sinhvien", MSSV_LienKet=data.MSSV)
    db.add(new_acc)
    db.commit()
    return {"status": "success"}

@router.put("/update/{mssv}")
def update_student(mssv: str, data: dict, db: Session = Depends(get_db)):
    sv = db.query(SinhVien).filter(SinhVien.MSSV == mssv).first()
    if not sv: raise HTTPException(status_code=404)
    
    sv.HoTen = data.get('HoTen', sv.HoTen)
    sv.MaKhoa = data.get('MaKhoa', sv.MaKhoa)
    sv.Nganh = data.get('Nganh', sv.Nganh)
    db.commit()
    return {"status": "success"}

@router.delete("/delete/{mssv}")
def delete_student(mssv: str, db: Session = Depends(get_db)):
    sv = db.query(SinhVien).filter(SinhVien.MSSV == mssv).first()
    if not sv: raise HTTPException(status_code=404)
    
    # Xóa sạch dữ liệu liên quan để tránh lỗi Foreign Key
    db.query(Advice).filter(Advice.MSSV == mssv).delete()
    db.query(RiskReasons).filter(RiskReasons.MSSV == mssv).delete()
    db.query(RiskThresholds).filter(RiskThresholds.MSSV == mssv).delete()
    db.query(RiskFeatures).filter(RiskFeatures.MSSV == mssv).delete()
    db.query(TaiKhoan).filter(TaiKhoan.MSSV_LienKet == mssv).delete()
    
    db.delete(sv) # Cuối cùng mới xóa sinh viên
    db.commit()
    return {"status": "success"}
@router.get("/{identifier}")
def get_student_info(identifier: str, db: Session = Depends(get_db)):
    # 1. Thử tìm sinh viên trực tiếp bằng MSSV
    student = db.query(SinhVien).filter(SinhVien.MSSV == identifier).first()
    
    # 2. Nếu không tìm thấy, thử tìm xem đây có phải là username đăng nhập không
    if not student:
        account = db.query(TaiKhoan).filter(TaiKhoan.username == identifier).first()
        if account and account.MSSV_LienKet:
            student = db.query(SinhVien).filter(SinhVien.MSSV == account.MSSV_LienKet).first()

    if not student:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông tin sinh viên.")
        
    return {
        "MSSV": student.MSSV,
        "HoTen": student.HoTen,
        "Nganh": student.Nganh,
        "TenKhoa": student.khoa.TenKhoa if student.khoa else "Chưa cập nhật"
    }