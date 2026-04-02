import streamlit as st
import pandas as pd
from utils import fetch_real_data

def inject_custom_css():
    st.markdown("""
    <style>
        .stApp { background-color: #f4f6f9; }
        .main-header { background-color: #154c8a; color: white; padding: 15px 20px; font-size: 22px; font-weight: bold; border-radius: 5px; margin-bottom: 20px; text-transform: uppercase; letter-spacing: 1px;}
        .page-title { color: #333; font-size: 20px; font-weight: bold; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

def show_student_data():
    inject_custom_css()
    st.markdown('<div class="main-header">HỆ THỐNG CẢNH BÁO RỦI RO HỌC TẬP</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">👥 Danh Sách Sinh Viên</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    col_space, col_search = st.columns([3, 1]) 

    with col_search:
        c1, c2 = st.columns([4, 1])
        with c1:
            search_input = st.text_input("Tìm kiếm", placeholder="Nhập MSSV...", label_visibility="collapsed")
        with c2:
            submit = st.button("🔍")

    search_query = search_input.strip()
    data = fetch_real_data()

    if data:
        df = pd.DataFrame(data)
        
        if search_query:
            df = df[df['MSSV'].str.contains(search_query, case=False, na=False)]

        if not df.empty:
            df['Rủi ro (%)'] = df['risk_score'].apply(lambda x: f"{x*100:.2f}%")
            
            # Đưa cột Lop vào danh sách hiển thị
            display_cols = ['MSSV', 'HoTen', 'Lop', 'Khoa', 'Nganh', 'Rủi ro (%)', 'risk_level']
            st.dataframe(df[display_cols], use_container_width=True)
        else:
            st.warning(f"Không tìm thấy sinh viên có MSSV: {search_query}")
    else:
        st.info("Chưa có dữ liệu sinh viên.")