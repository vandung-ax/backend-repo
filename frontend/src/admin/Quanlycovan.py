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

def show_teacher_mgmt():
    inject_custom_css()
    st.markdown('<div class="main-header">HỆ THỐNG CẢNH BÁO RỦI RO HỌC TẬP</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">👨‍🏫 Quản lý Cố vấn</div>', unsafe_allow_html=True)
    st.markdown("---")

    # Chia giao diện thành 2 Tab
    tab1, tab2 = st.tabs(["📋 Danh sách Cố vấn", "🏫 Phân công Lớp"])

    # ==========================================
    # TAB 1: QUẢN LÝ DANH SÁCH CỐ VẤN
    # ==========================================
    with tab1:
        st.write("### 📋 Danh sách Cố vấn hiện tại")
        try:
            # 1. Gọi API lấy dữ liệu và hiển thị bảng
            res_covan = requests.get(f"{API_BASE}/covan/all")
            if res_covan.status_code == 200:
                data_cv = res_covan.json()
                if len(data_cv) > 0:
                    df_cv = pd.DataFrame(data_cv)
                    # Đổi tên cột cho thân thiện với người dùng
                    df_display = df_cv[['Id_CoVan', 'TenCoVan', 'TenKhoa', 'MaKhoa']].rename(columns={
                        'Id_CoVan': 'ID',
                        'TenCoVan': 'Họ và Tên',
                        'TenKhoa': 'Trực thuộc Khoa',
                        'MaKhoa': 'Mã Khoa'
                    })
                    st.dataframe(df_display, use_container_width=True, hide_index=True)
                    
                    # --- CHỨC NĂNG XÓA ---
                    st.markdown("---")
                    st.write("**🗑️ Xóa Cố vấn**")
                    c1, c2 = st.columns([1, 2])
                    with c1:
                        delete_id = st.number_input("Nhập ID Cố vấn cần xóa:", min_value=1, step=1, key="del_adv_id")
                        if st.button("❌ Xác nhận xóa", type="primary", use_container_width=True):
                            # Gọi API xóa từ Backend (covanr.py)
                            res_del = requests.delete(f"{API_BASE}/covan/delete/{delete_id}")
                            if res_del.status_code == 200:
                                st.success(f"✅ Đã xóa cố vấn ID {delete_id} thành công!")
                                st.rerun()
                            else:
                                st.error("❌ Lỗi: Không tìm thấy ID hoặc Cố vấn này đang có ràng buộc dữ liệu.")
                    with c2:
                        st.info("💡 **Mẹo:** Bạn hãy nhìn cột **ID** ở bảng danh sách phía trên để nhập số chính xác trước khi bấm xóa.")

                else:
                    st.info("Chưa có dữ liệu Cố vấn. Hãy thêm mới ở bên dưới!")
            else:
                st.error("❌ Lỗi: Backend không phản hồi dữ liệu.")
        except Exception as e:
            st.error(f"❌ Lỗi kết nối Backend: {e}")

        st.markdown("---")
        # --- FORM THÊM MỚI ---
        st.write("### ➕ Thêm Cố vấn mới")
        try:
            res_khoa = requests.get(f"{API_BASE}/khoa-list")
            if res_khoa.status_code == 200:
                khoas = res_khoa.json()
                if khoas:
                    khoa_dict = {k['MaKhoa']: k['TenKhoa'] for k in khoas}
                    with st.form("form_add_covan"):
                        col_n, col_k = st.columns(2)
                        with col_n:
                            new_name = st.text_input("Họ và Tên Cố vấn (*):")
                        with col_k:
                            new_khoa = st.selectbox("Thuộc Khoa (*):", options=list(khoa_dict.keys()), format_func=lambda x: khoa_dict[x])
                        
                        submit_btn = st.form_submit_button("Lưu vào hệ thống", use_container_width=True)
                        if submit_btn:
                            if new_name.strip():
                                payload = {"TenCoVan": new_name.strip(), "MaKhoa": new_khoa}
                                res_add = requests.post(f"{API_BASE}/covan/add", json=payload)
                                if res_add.status_code == 200:
                                    st.success("✅ Đã thêm cố vấn thành công!")
                                    st.rerun()
                                else:
                                    st.error("❌ Lỗi khi gửi dữ liệu lên Backend.")
                            else:
                                st.warning("⚠️ Vui lòng nhập tên cố vấn.")
        except Exception:
            st.error("Không thể tải danh sách khoa để thêm cố vấn.")

    # ==========================================
    # TAB 2: PHÂN CÔNG LỚP (CHIA LỚP)
    # ==========================================
    with tab2:
        st.write("### 🏫 Thực hiện phân công lớp cho Cố vấn")
        try:
            res_khoa_assign = requests.get(f"{API_BASE}/khoa-list")
            if res_khoa_assign.status_code == 200:
                khoas_assign = res_khoa_assign.json()
                khoa_dict_assign = {k['MaKhoa']: k['TenKhoa'] for k in khoas_assign}
                
                selected_makhoa = st.selectbox(
                    "📌 Bước 1: Chọn Khoa quản lý lớp:", 
                    options=list(khoa_dict_assign.keys()), 
                    format_func=lambda x: khoa_dict_assign[x],
                    key="sel_k_assign"
                )

                if selected_makhoa:
                    # Lấy dữ liệu lớp và cố vấn của khoa
                    res_data = requests.get(f"{API_BASE}/assign-data/{selected_makhoa}").json()
                    covans_list = res_data.get("covans", [])
                    lops_list = res_data.get("lops", [])

                    if not covans_list:
                        st.warning("Khoa này chưa có cố vấn. Hãy thêm cố vấn ở Tab bên cạnh.")
                    elif not lops_list:
                        st.warning("Khoa này chưa có lớp. Hãy tải dữ liệu sinh viên lên trước.")
                    else:
                        df_lop_data = pd.DataFrame(lops_list)
                        cv_map = {cv['Id_CoVan']: cv['TenCoVan'] for cv in covans_list}
                        df_lop_data['Cố vấn hiện tại'] = df_lop_data['Id_CoVan'].map(cv_map).fillna("🔴 Chưa phân công")

                        c_act, c_view = st.columns([1, 1.5])
                        with c_act:
                            st.markdown("**⚙️ Phân bổ lớp**")
                            target_cv_id = st.selectbox(
                                "Chọn Cố vấn nhận lớp:", 
                                options=[cv['Id_CoVan'] for cv in covans_list],
                                format_func=lambda x: cv_map[x],
                                key="target_cv"
                            )
                            
                            # Tự động chọn những lớp mà cố vấn này đang quản lý
                            current_assigned = df_lop_data[df_lop_data['Id_CoVan'] == target_cv_id]['MaLop'].tolist()
                            
                            final_lops = st.multiselect(
                                "Chọn danh sách các lớp:", 
                                options=df_lop_data['MaLop'].tolist(),
                                default=current_assigned,
                                key="multi_lops"
                            )

                            if st.button("💾 Xác nhận lưu", type="primary", use_container_width=True):
                                p_load = {"id_covan": target_cv_id, "malop_list": final_lops}
                                r_save = requests.post(f"{API_BASE}/assign-lop", json=p_load)
                                if r_save.status_code == 200:
                                    st.success("✅ Cập nhật phân công thành công!")
                                    st.rerun()
                                else:
                                    st.error("❌ Lỗi khi lưu phân công.")

                        with c_view:
                            st.markdown("**📋 Tình trạng phân lớp**")
                            st.dataframe(df_lop_data[['MaLop', 'Cố vấn hiện tại']], use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Lỗi: {e}")