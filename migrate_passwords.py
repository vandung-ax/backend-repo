"""
Script chuyen doi tat ca mat khau plain text trong database sang bcrypt hash.
Chay 1 lan duy nhat sau khi cap nhat code.

Cach chay: python migrate_passwords.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.student_risk import TaiKhoan
from app.utils.password import hash_password

def migrate():
    db = SessionLocal()
    try:
        accounts = db.query(TaiKhoan).all()
        count = 0
        for acc in accounts:
            # Check if password is already bcrypt hashed (starts with $2b$)
            if acc.password and not acc.password.startswith("$2b$"):
                # Truncate to 72 bytes (bcrypt limit)
                pw = acc.password[:72]
                print(f"  Hashing password for account: {acc.username} (role: {acc.role})")
                acc.password = hash_password(pw)
                count += 1
        
        db.commit()
        print(f"\n[OK] Done! Converted {count}/{len(accounts)} accounts to bcrypt hash.")
    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 50)
    print("[LOCK] MIGRATE PASSWORDS TO BCRYPT HASH")
    print("=" * 50)
    migrate()
