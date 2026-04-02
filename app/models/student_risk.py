from sqlalchemy import JSON, Column, Integer, String, Float, ForeignKey, TIMESTAMP, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base 
from sqlalchemy import ForeignKey
class Khoa(Base):
    __tablename__ = "khoa"
    MaKhoa = Column(String(20), primary_key=True)
    TenKhoa = Column(String(100))
    
    sinhviens = relationship("SinhVien", back_populates="khoa")
    covans = relationship("CoVan", back_populates="khoa")
class Lop(Base):
    __tablename__ = "lop"
    MaLop = Column(String(20), primary_key=True)
    TenLop = Column(String(100), nullable=False)
    MaKhoa = Column(String(20), ForeignKey("khoa.MaKhoa"))
    Id_CoVan = Column(Integer, ForeignKey("covan.Id_CoVan"), nullable=True)

    khoa = relationship("Khoa", backref="lops")
    covan = relationship("CoVan", backref="lops")
    sinhviens = relationship("SinhVien", back_populates="lop_hoc")
class SinhVien(Base):
    __tablename__ = "sinhvien"
    MSSV = Column(String(50), primary_key=True)
    HoTen = Column(String(100))
    MaKhoa = Column(String(20), ForeignKey("khoa.MaKhoa"))
    Nganh = Column(String(100))
    MaLop = Column(String(20), ForeignKey("lop.MaLop"), nullable=True)
    Id_CoVan = Column(Integer, ForeignKey("covan.Id_CoVan"), nullable=True)

    khoa = relationship("Khoa", back_populates="sinhviens")
    lop_hoc = relationship("Lop", back_populates="sinhviens")
    features = relationship("RiskFeatures", back_populates="sinhvien")
    thresholds = relationship("RiskThresholds", back_populates="sinhvien")
    account = relationship("TaiKhoan", back_populates="sinhvien", uselist=False)
    covan = relationship("CoVan", backref="sinhviens")
class CoVan(Base):
    __tablename__ = "covan"
    Id_CoVan = Column(Integer, primary_key=True, autoincrement=True)
    TenCoVan = Column(String(100))
    MaKhoa = Column(String(20), ForeignKey("khoa.MaKhoa"))

    khoa = relationship("Khoa", back_populates="covans")
    account = relationship("TaiKhoan", back_populates="covan", uselist=False)

class TaiKhoan(Base):
    __tablename__ = "taikhoan"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True)
    password = Column(String(255))
    role = Column(Enum('admin', 'covan', 'sinhvien'))
    MSSV_LienKet = Column(String(50), ForeignKey("sinhvien.MSSV"), nullable=True)
    Id_CoVan_LienKet = Column(Integer, ForeignKey("covan.Id_CoVan"), nullable=True)
    sinhvien = relationship("SinhVien", back_populates="account")
    covan = relationship("CoVan", back_populates="account")

class RiskFeatures(Base):
    __tablename__ = "risk_features"
    id = Column(Integer, primary_key=True, autoincrement=True)
    MSSV = Column(String(50), ForeignKey("sinhvien.MSSV"))
    Attendance = Column(Float)
    Hours_Studied = Column(Float)
    Previous_Scores = Column(Float)
    Access_to_Resources = Column(String(50))
    Motivation_Level = Column(String(50))
    Family_Income = Column(String(50))
    Peer_Influence = Column(String(50))
    Distance_from_Home = Column(String(50))
    Extracurricular_Activities = Column(String(50))
    Sleep_Hours = Column(Float)
    Teacher_Quality = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=func.now())

    sinhvien = relationship("SinhVien", back_populates="features")

class RiskThresholds(Base):
    __tablename__ = "risk_threshols"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    MSSV = Column(String(50), ForeignKey("sinhvien.MSSV"))
    
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String(50), nullable=False)
    ai_explanation_path = Column(JSON, nullable=True)
    batch_id = Column(Integer, ForeignKey("prediction_batches.id"), nullable=True)   # ← Quan trọng
    
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    sinhvien = relationship("SinhVien", back_populates="thresholds")
    batch = relationship("PredictionBatches", back_populates="thresholds")   # ← Phải khớp
class RiskReasons(Base):
    __tablename__ = "risk_reasons"
    id = Column(Integer, primary_key=True, autoincrement=True)
    MSSV = Column(String(50), ForeignKey("sinhvien.MSSV"))
    reason_text = Column(Text)

class Advice(Base):
    __tablename__ = "advices"
    id = Column(Integer, primary_key=True, autoincrement=True)
    MSSV = Column(String(50), ForeignKey("sinhvien.MSSV"))
    reason_id = Column(Integer, ForeignKey("risk_reasons.id"))
    advice_text = Column(Text)

# Thêm vào app/models/student_risk.py

class PredictionBatches(Base):
    __tablename__ = "prediction_batches"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tree_rules_for_professor = Column(Text, nullable=False)
    uploaded_by = Column(Integer, ForeignKey("taikhoan.id"), nullable=True) # <-- THÊM DÒNG NÀY # Lưu cấu trúc cây AI
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Khai báo quan hệ để có thể truy xuất từ Batch ra các kết quả dự báo
    thresholds = relationship("RiskThresholds", back_populates="batch")