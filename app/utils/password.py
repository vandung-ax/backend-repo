"""
Tien ich ma hoa mat khau bang bcrypt.
Su dung trong toan bo he thong xac thuc.
"""
import bcrypt

def hash_password(plain_password: str) -> str:
    """Ma hoa mat khau thanh bcrypt hash."""
    # Bcrypt gioi han 72 bytes
    pw_bytes = plain_password.encode("utf-8")[:72]
    hashed = bcrypt.hashpw(pw_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """So sanh mat khau nhap vao voi hash da luu."""
    pw_bytes = plain_password.encode("utf-8")[:72]
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(pw_bytes, hashed_bytes)
