import streamlit as st
import requests
import extra_streamlit_components as stx
import time
from streamlit_option_menu import option_menu

# 1. Cấu hình trang đầu tiên
st.set_page_config(page_title="Hệ thống dự báo rủi ro", layout="wide", initial_sidebar_state="expanded")

def inject_global_css():
    st.markdown("""
    <style>
        /* 1. CHỈ ẨN NÚT DEPLOY VÀ MENU 3 CHẤM, GIỮ LẠI NÚT MỞ SIDEBAR (>) */
        .stAppDeployButton {
            display: none !important;
        }
        [data-testid="stToolbar"] {
            display: none !important;
        }
        
        /* Làm cho nền header trong suốt để không bị một dải màu trắng chắn ngang */
        [data-testid="stHeader"] {
            background-color: transparent !important;
        }
        
        /* 2. ÉP KHOẢNG TRẮNG TRÊN CÙNG SÁT RẠT LÊN TRẦN */
        .block-container {
            padding-top: 0rem !important; 
            padding-bottom: 0rem !important;
            margin-top: 0rem !important;
        }

        /* Tùy chỉnh nền Sidebar */
        [data-testid="stSidebar"] {
            background-color: #f4f7f9;
        }
        
        /* Box thông tin User trên Sidebar */
        .user-profile-box {
            display: flex;
            align-items: center;
            padding: 15px;
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            margin-bottom: 20px;
            border: 1px solid #e1e4e8;
        }
        .user-avatar {
            width: 45px;
            height: 45px;
            background-color: #154c8a;
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            font-weight: bold;
            margin-right: 12px;
        }
        .user-info { display: flex; flex-direction: column; }
        .user-name { font-weight: 700; color: #1e293b; font-size: 15px; margin-bottom: 2px; }
        .user-role { font-size: 11px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }

        /* Nút Đăng xuất */
        [data-testid="stSidebar"] .stButton > button {
            width: 100%;
            background-color: white !important;
            color: #1e293b !important;
            border: 1px solid #cbd5e1 !important;
            border-radius: 8px !important;
            padding: 8px 10px !important;
            font-weight: 600;
            transition: all 0.3s;
        }
        [data-testid="stSidebar"] .stButton > button:hover {
            border-color: #154c8a !important;
            color: #154c8a !important;
            background-color: #f0f7ff !important;
        }
    </style>
    """, unsafe_allow_html=True)

# Gọi CSS ngay từ đầu
inject_global_css()

# 2. Khởi tạo Cookie Manager
cookie_manager = stx.CookieManager(key="main_cookie_manager")

def check_login():
    if "user_data" in st.session_state:
        return True

    saved_user = None
    if not st.session_state.get("just_logged_out", False):
        for _ in range(3):
            saved_user = cookie_manager.get(cookie="user_login")
            if saved_user:
                break
            time.sleep(0.2)

    if saved_user:
        st.session_state.user_data = saved_user
        st.session_state.user_role = saved_user['role']
        # CHÌA KHÓA TRỊ BỆNH F5 Ở ĐÂY 👇
        # Ép reload lại luồng chạy ngay sau khi đọc cookie thành công để Menu không bị crash
        st.rerun() 
        return True

    # --- FORM ĐĂNG NHẬP (Canh giữa màn hình) ---
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><br><h2 style='text-align: center; color: #154c8a;'>ĐĂNG NHẬP HỆ THỐNG</h2><hr>", unsafe_allow_html=True)
        with st.form("login_form"):
            username = st.text_input("Tên đăng nhập", placeholder="Nhập tên đăng nhập...")
            password = st.text_input("Mật khẩu", type="password", placeholder="Nhập mật khẩu...")
            submit = st.form_submit_button("🚀 Đăng nhập", use_container_width=True)
            
            if submit:
                try:
                    response = requests.post(
                        "http://localhost:8000/api/auth/login",
                        json={"username": username, "password": password}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.user_data = data
                        st.session_state.user_role = data['role']
                        st.session_state["just_logged_out"] = False 
                        
                        cookie_manager.set("user_login", data, key="save_cookie")
                        
                        st.success(f"✅ Chào mừng {data['display_name']}!")
                        time.sleep(0.5) 
                        st.rerun()
                    else:
                        st.error("❌ Sai tài khoản hoặc mật khẩu!")
                except Exception as e:
                    st.error(f"⚠️ Lỗi kết nối Backend: {e}")
    return False

def logout():
    st.session_state["just_logged_out"] = True
    cookie_manager.delete("user_login") 
    
    for key in list(st.session_state.keys()):
        if key != "just_logged_out":
            del st.session_state[key]
            
    st.info("🔄 Đang đăng xuất an toàn...")
    time.sleep(0.6)
    st.rerun()

def render_user_profile(name, role):
    # Lấy chữ cái đầu làm Avatar
    initial = name[0].upper() if name else "U"
    html = f"""
    <div class="user-profile-box">
        <div class="user-avatar">{initial}</div>
        <div class="user-info">
            <span class="user-name">{name}</span>
            <span class="user-role">Vai trò: {role}</span>
        </div>
    </div>
    """
    st.sidebar.markdown(html, unsafe_allow_html=True)

# ---------------- LUỒNG THỰC THI CHÍNH ----------------
if check_login():
    role = st.session_state.user_role
    user_info = st.session_state.user_data
    
    # Hiển thị thông tin cơ bản trên Sidebar
    render_user_profile(user_info['display_name'], role)

    # ---------------- PHÂN QUYỀN VAI TRÒ ----------------
    
    # --- ADMIN ---
    if role == "admin":
        with st.sidebar:
            menu = option_menu(
                menu_title="CHỨC NĂNG",
                options=["Tổng quan hệ thống", "Quản lý cố vấn", "Quản lý sinh viên", "Quản lý tài khoản", "Tải dữ liệu", "Huấn luyện AI"],
                icons=["bar-chart-line", "person-workspace", "mortarboard", "person-vcard", "cloud-upload", "robot"],
                menu_icon="cast",
                default_index=0,
                key="admin_menu",
                styles={
                    "container": {"padding": "0!important", "background-color": "transparent"},
                    "icon": {"color": "#154c8a", "font-size": "18px"}, 
                    "nav-link": {"font-size": "15px", "text-align": "left", "margin":"5px", "--hover-color": "#e2e8f0"},
                    "nav-link-selected": {"background-color": "#154c8a", "color": "white"},
                }
            )
        
        if menu == "Quản lý cố vấn":
            from src.admin.Quanlycovan import show_teacher_mgmt
            show_teacher_mgmt()
        elif menu == "Quản lý sinh viên":
            from src.admin.Quanlysinhvien import show_student_mgmt
            show_student_mgmt()
        elif menu == "Quản lý tài khoản":
            from src.admin.Quanlytaikhoan import show_account_mgmt
            show_account_mgmt()
        elif menu == "Tải dữ liệu":
            from src.admin.uploadfiledb import show_upload_predict
            show_upload_predict()
        elif menu == "Tổng quan hệ thống":
            from src.admin.Thongkead import show_statistics
            show_statistics()
        elif menu == "Huấn luyện AI":
            from src.admin.retrain_md import show_retrain_system
            show_retrain_system()

    # --- CỐ VẤN (GIÁO VIÊN) ---
    elif role == "covan":
        with st.sidebar:
            menu = option_menu(
                menu_title="CHỨC NĂNG",
                options=["Tổng quan", "Thống kê", "Danh sách sinh viên", "Sinh viên nguy cơ cao"],
                icons=["house", "graph-up", "list-task", "exclamation-triangle"],
                menu_icon="cast",
                default_index=0,
                key="covan_menu",
                styles={
                    "container": {"padding": "0!important", "background-color": "transparent"},
                    "icon": {"color": "#154c8a", "font-size": "18px"}, 
                    "nav-link": {"font-size": "15px", "text-align": "left", "margin":"5px", "--hover-color": "#e2e8f0"},
                    "nav-link-selected": {"background-color": "#154c8a", "color": "white"},
                }
            )
        
        if menu == "Tổng quan":
            from src.covan.tongquan import show_overview
            show_overview()
        elif menu == "Thống kê":
            from src.covan.thongke import show_statistics
            show_statistics()
        elif menu == "Danh sách sinh viên":
            from src.covan.dulieusinhvie import show_student_data
            show_student_data()
        elif menu == "Sinh viên nguy cơ cao":
            from src.covan.sinhviennguycocao import show_at_risk_students
            show_at_risk_students()

    # --- SINH VIÊN ---
    elif role == "sinhvien":
        with st.sidebar:
            menu = option_menu(
                menu_title="CHỨC NĂNG",
                options=["Thông tin cá nhân", "Phân tích rủi ro"],
                icons=["person-bounding-box", "shield-exclamation"],
                menu_icon="cast",
                default_index=0,
                key="sinhvien_menu",
                styles={
                    "container": {"padding": "0!important", "background-color": "transparent"},
                    "icon": {"color": "#154c8a", "font-size": "18px"}, 
                    "nav-link": {"font-size": "15px", "text-align": "left", "margin":"5px", "--hover-color": "#e2e8f0"},
                    "nav-link-selected": {"background-color": "#154c8a", "color": "white"},
                }
            )
        
        if menu == "Thông tin cá nhân":
            from src.sinhvien.Thongtincanhan import show_personal_info
            show_personal_info(user_info['username']) 
        elif menu == "Phân tích rủi ro":
            from src.sinhvien.Thongtinruiro import show_risk_analysis
            show_risk_analysis(user_info['username']) 

    # ---------------- NÚT ĐĂNG XUẤT CHUNG ----------------
    st.sidebar.markdown("<br><br>", unsafe_allow_html=True) # Đẩy nút đăng xuất xuống dưới một chút
    if st.sidebar.button("🚪 Đăng xuất", use_container_width=True):
        logout()