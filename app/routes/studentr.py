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
    # 1. Kiểm tra xem MSSV đã tồn tại trong bảng SinhVien chưa
    if db.query(SinhVien).filter(SinhVien.MSSV == data.MSSV).first():
        raise HTTPException(status_code=400, detail="MSSV đã tồn tại trong hệ thống!")

    # 2. Kiểm tra xem Tài Khoản đã tồn tại chưa (đề phòng lỗi rác từ trước)
    if db.query(TaiKhoan).filter(TaiKhoan.username == data.username).first():
        raise HTTPException(status_code=400, detail=f"Tài khoản đăng nhập '{data.username}' đã có người sử dụng!")

    try:
        # 3. CHỈ THÊM SINH VIÊN (Tuyệt đối không code phần thêm TaiKhoan ở đây)
        new_sv = SinhVien(
            MSSV=data.MSSV,
            HoTen=data.HoTen,
            MaKhoa=data.MaKhoa,
            Nganh=data.Nganh,
            MaLop=data.Lop,
        )
        db.add(new_sv)
        
        # 4. Lệnh commit() này sẽ chốt giao dịch. 
        # Ngay lúc này, MySQL sẽ nhận dữ liệu SinhVien -> kích hoạt Trigger -> tự động lưu thêm TaiKhoan.
        db.commit()
        
        return {"status": "success"}
        
    except Exception as e:
        db.rollback() # Nếu có lỗi gì khác, hủy thao tác để bảo vệ DB
        raise HTTPException(status_code=500, detail=f"Lỗi cơ sở dữ liệu: {str(e)}")
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