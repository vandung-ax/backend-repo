import streamlit as st
import requests
import pandas as pd

BASE_URL = "http://127.0.0.1:8000"

def fetch_all_student_data():
    try:
        role = st.session_state.user_role
        user_id = st.session_state.user_data.get('id')

        if role == 'admin' or role == 'sinhvien':
            url = f"{BASE_URL}/api/data/all-results"
        else:
            url = f"{BASE_URL}/api/data/all-results?user_id={user_id}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if not data: return pd.DataFrame()
            
            df_raw = pd.DataFrame(data)
            
            if 'details' in df_raw.columns:
                details_df = pd.json_normalize(df_raw['details'])
                df_final = pd.concat([df_raw.drop(columns=['details']), details_df], axis=1)
            else:
                df_final = df_raw
            
            numeric_cols = ['risk_score', 'attendance', 'hours_studied', 'previous_scores', 'sleep_hours']
            for col in numeric_cols:
                if col in df_final.columns:
                    df_final[col] = pd.to_numeric(df_final[col], errors='coerce')
            
            return df_final
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

def fetch_real_data(scope="khoa"):
    if 'user_data' not in st.session_state:
        return []
    
    user_id = st.session_state.user_data.get('id')
    try:
        response = requests.get(f"{BASE_URL}/api/data/all-results?user_id={user_id}&scope={scope}")
        if response.status_code == 200:
            return response.json()
        return []
    except requests.exceptions.RequestException as e:
        st.error(f"Lỗi kết nối Backend: {e}")
        return []

def fetch_advisors():
    try:
        response = requests.get(f"{BASE_URL}/api/covan/all")
        return pd.DataFrame(response.json()) if response.status_code == 200 else pd.DataFrame()
    except: return pd.DataFrame()

def fetch_departments():
    try:
        response = requests.get(f"{BASE_URL}/api/admin/khoa/all")
        return response.json() if response.status_code == 200 else []
    except: return []

def manage_advisor_api(method, data=None, advisor_id=None):
    try:
        if method == "POST": return requests.post(f"{BASE_URL}/api/covan/add", json=data)
        if method == "PUT": return requests.put(f"{BASE_URL}/api/covan/update/{advisor_id}", json=data)
        if method == "DELETE": return requests.delete(f"{BASE_URL}/api/covan/delete/{advisor_id}")
    except: return None

def fetch_students():
    try:
        response = requests.get(f"{BASE_URL}/api/student/all")
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Lỗi API Sinh Viên: {e}")
        return pd.DataFrame()

def manage_student_api(method, data=None, mssv=None):
    try:
        url_map = {
            "POST": f"{BASE_URL}/api/student/add",
            "PUT": f"{BASE_URL}/api/student/update/{mssv}",
            "DELETE": f"{BASE_URL}/api/student/delete/{mssv}"
        }
        if method == "POST": return requests.post(url_map[method], json=data)
        if method == "PUT": return requests.put(url_map[method], json=data)
        if method == "DELETE": return requests.delete(url_map[method])
    except: return None

def fetch_accounts():
    try:
        response = requests.get(f"{BASE_URL}/api/account/all")
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Lỗi API Tài khoản: {e}")
        return pd.DataFrame()

def manage_account_api(method, data=None, account_id=None):
    try:
        url_map = {
            "POST": f"{BASE_URL}/api/account/add",
            "PUT": f"{BASE_URL}/api/account/update/{account_id}",
            "DELETE": f"{BASE_URL}/api/account/delete/{account_id}"
        }
        if method == "POST": return requests.post(url_map[method], json=data)
        if method == "PUT": return requests.put(url_map[method], json=data)
        if method == "DELETE": return requests.delete(url_map[method])
    except: 
        return None

def fetch_or_generate_advice(mssv, risk_reasons=""):
    try:
        payload = {"risk_reasons": risk_reasons}
        response = requests.post(f"{BASE_URL}/api/advice/generate/{mssv}", json=payload)
        
        if response.status_code == 200:
            return response.json().get("advice")
        return f"Lỗi: {response.json().get('detail')}"
    except Exception as e:
        return f"Lỗi kết nối Backend: {str(e)}"

def manage_retrain_api(file):
    try:
        files = {"file": (file.name, file.getvalue(), "text/csv")}
        response = requests.post(f"{BASE_URL}/api/retrain-model", files=files)
        return response
    except Exception as e:
        st.error(f"Lỗi kết nối: {e}")
        return None

def fetch_train_history():
    """Lấy danh sách các phiên bản mô hình đã huấn luyện"""
    try:
        response = requests.get(f"{BASE_URL}/api/data/train-history")
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Lỗi gọi API lịch sử train: {e}")
        return []

def sync_tree_from_ai(user_id):
    """Gọi API Backend để ra lệnh kéo cây mới nhất từ Render về"""
    try:
        response = requests.post(f"{BASE_URL}/api/sync-latest-tree?user_id={user_id}")
        if response.status_code == 200:
            return True, response.json().get("message")
        return False, response.json().get("detail", "Lỗi không xác định")
    except Exception as e:
        return False, str(e)

# --- THÊM HÀM MỚI LẤY SỐ LIỆU TỔNG QUAN ---
def fetch_dashboard_stats():
    """Lấy số lượng tổng Sinh viên, Cố vấn, Tài khoản"""
    try:
        response = requests.get(f"{BASE_URL}/api/data/dashboard-stats")
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Lỗi kết nối Backend lấy số liệu: {e}")
    return {"total_sinhvien": 0, "total_covan": 0, "total_taikhoan": 0}