import streamlit as st
import pandas as pd
from utils import fetch_accounts, manage_account_api

def show_account_mgmt():
    st.markdown("""
    <style>
        .main-header { background-color: #154c8a; color: white; padding: 15px 20px; font-size: 22px; font-weight: bold; border-radius: 5px; margin-bottom: 20px;}
        .page-title { color: #333; font-size: 20px; font-weight: bold; margin-bottom: 15px; }
        .stButton > button { background-color: #154c8a !important; color: white !important; border-radius: 5px !important; border: none !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-header">HỆ THỐNG CẢNH BÁO RỦI RO HỌC TẬP</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">Quản Lý Tài Khoản</div>', unsafe_allow_html=True)

    df_accounts = fetch_accounts()
    tab1, tab2 = st.tabs(["📋 Danh Sách Tài Khoản", "➕ Tạo Tài Khoản"])

    with tab1:
        col_search, col_filter = st.columns([2, 1])
        with col_search:
            search_term = st.text_input("🔍 Tìm kiếm:", placeholder="Tên đăng nhập hoặc ID...")
        with col_filter:
            role_filter = st.selectbox("Lọc vai trò:", ["Tất cả", "admin", "covan", "sinhvien"])

        if not df_accounts.empty:
            df_display = df_accounts.copy()
            if role_filter != "Tất cả":
                df_display = df_display[df_display['role'] == role_filter]
            if search_term:
                df_display = df_display[
                    df_display['username'].str.contains(search_term, case=False, na=False) |
                    df_display['MSSV_LienKet'].astype(str).str.contains(search_term, case=False, na=False) |
                    df_display['Id_CoVan_LienKet'].astype(str).str.contains(search_term, case=False, na=False)
                ]

            st.caption(f"Tổng số: {len(df_display)} tài khoản")
            desired_order = ["id", "username", "password", "role", "MSSV_LienKet", "Id_CoVan_LienKet"]
            df_display_ordered = df_display[[c for c in desired_order if c in df_display.columns]]
            st.dataframe(df_display_ordered, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            col_edit, col_del = st.columns(2)
            
            with col_edit:
                st.subheader("✏️ Chỉnh sửa")
                selected_id = st.selectbox("Chọn ID tài khoản:", df_display["id"].tolist(), key="sb_edit_acc")
                current_info = df_display[df_display["id"] == selected_id].iloc[0]
                
                with st.form("form_edit_taikhoan"):
                    new_role = st.selectbox("Vai trò:", options=["admin", "covan", "sinhvien"], index=["admin", "covan", "sinhvien"].index(current_info["role"]))
                    new_password = st.text_input("Mật khẩu mới (Để trống nếu không đổi):", type="password")
                    new_mssv = st.text_input("MSSV Liên Kết:", value=str(current_info.get("MSSV_LienKet", "")) if pd.notna(current_info.get("MSSV_LienKet")) else "")
                    new_idcovan = st.text_input("ID Cố Vấn Liên Kết:", value=str(current_info.get("Id_CoVan_LienKet", "")) if pd.notna(current_info.get("Id_CoVan_LienKet")) else "")

                    if st.form_submit_button("Lưu thay đổi"):
                        payload = {"role": new_role, "MSSV_LienKet": new_mssv if new_mssv else None, "Id_CoVan_LienKet": int(new_idcovan) if new_idcovan else None}
                        if new_password: payload["password"] = new_password
                        res = manage_account_api("PUT", data=payload, account_id=selected_id)
                        if res and res.status_code == 200: st.success("✅ Cập nhật thành công!"); st.rerun()

            with col_del:
                st.subheader("🗑️ Xóa")
                del_id = st.selectbox("Chọn ID cần xóa:", df_display["id"].tolist(), key="sb_del_acc")
                if st.button("Xóa tài khoản", use_container_width=True):
                    res = manage_account_api("DELETE", account_id=del_id)
                    if res and res.status_code == 200: st.success("✅ Đã xóa!"); st.rerun()

    with tab2:
        st.markdown('### 🖊️ Nhập thông tin tài khoản')
        with st.form("form_add_taikhoan"):
            col1, col2 = st.columns(2)
            with col1:
                add_username = st.text_input("Tên đăng nhập (*):")
                add_role = st.selectbox("Vai trò (*):", options=["admin", "covan", "sinhvien"])
                add_mssv = st.text_input("MSSV Liên Kết:")
            with col2:
                add_password = st.text_input("Mật khẩu (*):", type="password")
                st.write("") # Spacer
                st.write("")
                add_idcovan = st.text_input("ID Cố Vấn Liên Kết:")
            
            if st.form_submit_button("➕ Thêm vào hệ thống"):
                if add_username and add_password:
                    payload = {"username": add_username, "password": add_password, "role": add_role, "MSSV_LienKet": add_mssv if add_mssv else None, "Id_CoVan_LienKet": int(add_idcovan) if add_idcovan else None}
                    res = manage_account_api("POST", data=payload)
                    if res and res.status_code in [200, 201]: st.success("✅ Đã thêm!"); st.rerun()
                    else: st.error("❌ Có lỗi xảy ra.")
                else: st.error("Vui lòng nhập đủ user/pass.")