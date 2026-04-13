from sqlalchemy import create_engine, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os

# Thay đổi thông tin theo MySQL của bạn (user, password, host, port)
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "mysql+mysqlconnector://root:root@localhost:3306/student_risk_mgmt")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()