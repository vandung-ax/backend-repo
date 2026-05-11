import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.student_risk import TaiKhoan
from app.utils.password import verify_password

def test_login(username, password):
    db = SessionLocal()
    try:
        user = db.query(TaiKhoan).filter(TaiKhoan.username == username).first()
        if not user:
            print(f"User {username} not found")
            return
        
        print(f"User: {user.username}")
        print(f"Stored Hash: {user.password}")
        print(f"Starts with $2b$: {user.password.startswith('$2b$')}")
        
        is_valid = verify_password(password, user.password)
        print(f"Password '{password}' valid: {is_valid}")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_login("admin", "admin") # default password for admin maybe? Or we can check what the hash represents.
