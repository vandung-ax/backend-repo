import streamlit as st
import pandas as pd
import requests

API_BASE = "http://127.0.0.1:8000/api"

def inject_custom_css():
    st.markdown("""
    <style>
        .stApp { background-color: #f4f6f9; }
        .main-header { background-color: #154c8a; color: white; padding: 15px 20px; font-size: 22px; font-weight: bold; border-radius: 5px; margin-bottom: 20px; text-transform: uppercase; letter-spacing: 1px;}
        .page-title { color: #333; font-size: 20px; font-weight: bold; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

def show_student_mgmt():
    inject_custom_css()
    st.markdown('<div class="main-header">HỆ THỐNG CẢNH BÁO RỦI RO HỌC TẬP</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">👨‍🎓 Quản lý Sinh viên</div>', unsafe_allow_html=True)
    st.markdown("---")

    tab1, tab2 = st.tabs(["📋 Danh sách Sinh viên", "➕ Thêm Sinh viên mới"])

    # ==========================================
    # TAB 1: DANH SÁCH & XÓA SINH VIÊN
    # ==========================================
    with tab1:
        st.write("### 📋 Danh sách sinh viên toàn trường")
        
        # Thanh tìm kiếm
        search_term = st.text_input("🔍 Tìm kiếm:", placeholder="Nhập MSSV hoặc Tên sinh viên...")
        
        try:
            res_students = requests.get(f"{API_BASE}/student/all")
            if res_students.status_code == 200:
                data_sv = res_students.json()
                
                if len(data_sv) > 0:
                    df_sv = pd.DataFrame(data_sv)
                    
                    # Lọc dữ liệu theo từ khóa tìm kiếm
                    if search_term:
                        mask = df_sv['HoTen'].str.contains(search_term, case=False, na=False) | \
                               df_sv['MSSV'].astype(str).str.contains(search_term, case=False, na=False)
                        df_display = df_sv[mask]
                    else:
                        df_display = df_sv
                    
                    if not df_display.empty:
                        # Làm đẹp tên cột trước khi hiển thị
                        df_display = df_display.rename(columns={
                            'MSSV': 'Mã SV',
                            'HoTen': 'Họ và Tên',
                            'TenKhoa': 'Khoa',
                            'MaKhoa': 'Mã Khoa',
                            'Nganh': 'Ngành học'
                        })
                        st.dataframe(df_display, use_container_width=True, hide_index=True)
                        
                        # --- Tính năng Xóa sinh viên ---
                        st.markdown("---")
                        st.write("**🗑️ Xóa Sinh Viên**")
                        col_del, _ = st.columns([1, 2])
                        with col_del:
                            del_mssv = st.text_input("Nhập MSSV cần xóa:")
                            if st.button("❌ Xác nhận xóa", type="primary"):
                                if del_mssv.strip():
                                    res_del = requests.delete(f"{API_BASE}/student/delete/{del_mssv.strip()}")
                                    if res_del.status_code == 200:
                                        st.success("✅ Đã xóa sinh viên thành công!")
                                        st.rerun()
                                    else:
                                        st.error("❌ Xóa thất bại. Không tìm thấy MSSV hoặc lỗi Server.")
                                else:
                                    st.warning("⚠️ Vui lòng nhập MSSV!")
                    else:
                        st.info("Không tìm thấy sinh viên nào khớp với từ khóa.")
                else:
                    st.info("Chưa có dữ liệu Sinh viên. Hãy tải file CSV lên hoặc thêm mới bằng tay.")
            else:
                st.error(f"❌ Lỗi Backend: {res_students.text}")
        except Exception as e:
            st.error(f"❌ Lỗi kết nối Backend: {e}")

    # ==========================================
    # TAB 2: THÊM SINH VIÊN MỚI
    # ==========================================
    with tab2:
        st.subheader("📝 Nhập thông tin sinh viên")
        try:
            # Lấy trước danh sách Khoa và Cố vấn để đưa vào Form
            res_khoa = requests.get(f"{API_BASE}/khoa-list")
            res_covan = requests.get(f"{API_BASE}/covan/all")
            
            khoas = res_khoa.json() if res_khoa.status_code == 200 else []
            covans = res_covan.json() if res_covan.status_code == 200 else []
            
            khoa_dict = {k['MaKhoa']: k['TenKhoa'] for k in khoas}
            covan_dict = {cv['Id_CoVan']: f"{cv['TenCoVan']} (Khoa {cv['MaKhoa']})" for cv in covans}

            if not khoas:
                st.warning("⚠️ Chưa có Khoa nào trong hệ thống, không thể thêm sinh viên!")
            else:
                with st.form("form_add_sinhvien"):
                    col1, col2 = st.columns(2)
                    with col1:
                        add_mssv = st.text_input("Mã số sinh viên (MSSV) (*):")
                        add_name = st.text_input("Họ và Tên (*):")
                        add_dept = st.selectbox("Thuộc Khoa (*):", options=list(khoa_dict.keys()), format_func=lambda x: khoa_dict.get(x, x))
                        add_nganh = st.text_input("Ngành học:")
                        add_lop = st.text_input("Lớp (Có thể để trống):")
                        
                    with col2:
                        add_idcovan = st.selectbox("Phân công Cố Vấn:", options=[None] + list(covan_dict.keys()), format_func=lambda x: "🔴 Chưa phân công" if x is None else covan_dict.get(x, x))
                        st.markdown("---")
                        st.write("**Tài khoản đăng nhập hệ thống**")
                        add_user = st.text_input("Tên đăng nhập (*):", placeholder="Thường lấy luôn MSSV")
                        add_pw = st.text_input("Mật khẩu (*):", type="password")
                
                    submit_btn = st.form_submit_button("➕ Lưu vào hệ thống", use_container_width=True)
                    
                    if submit_btn:
                        if add_mssv and add_name and add_user and add_pw:
                            payload = {
                                "MSSV": add_mssv,
                                "HoTen": add_name,
                                "MaKhoa": add_dept,
                                "Nganh": add_nganh,
                                "Lop": add_lop,
                                "Id_CoVan": add_idcovan,
                                "username": add_user,
                                "password": add_pw
                            }
                            res_add = requests.post(f"{API_BASE}/student/add", json=payload)
                            
                            if res_add.status_code == 200:
                                st.success(f"✅ Đã thêm sinh viên {add_name} thành công!")
                                st.rerun()
                            else:
                                st.error(f"❌ Lỗi khi thêm: {res_add.json().get('detail', res_add.text)}")
                        else:
                            st.warning("⚠️ Vui lòng nhập đầy đủ các trường có dấu (*)")
        except Exception as e:
            st.error(f"❌ Lỗi tải Form: {e}")