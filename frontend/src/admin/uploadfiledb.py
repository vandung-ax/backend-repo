import streamlit as st
import pandas as pd
import requests

def show_upload_predict():
    st.markdown("""
    <style>
        .main-header { background-color: #154c8a; color: white; padding: 15px 20px; font-size: 22px; font-weight: bold; border-radius: 5px; margin-bottom: 20px;}
        .page-title { color: #333; font-size: 20px; font-weight: bold; margin-bottom: 5px; }
        .stButton > button { background-color: #154c8a !important; color: white !important; border-radius: 5px !important; border: none !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-header">HỆ THỐNG CẢNH BÁO RỦI RO HỌC TẬP</div>', unsafe_allow_html=True)
    
    admin_name = st.session_state.user_data.get('display_name', 'Quản trị viên')
    st.markdown(f'<div class="page-title">Tải Dữ Liệu & Dự Báo (Admin: {admin_name})</div>', unsafe_allow_html=True)
    st.caption("💡 File CSV cần có: MSSV, Họ Tên, Khoa, Ngành và 11 cột đặc trưng hệ thống.")
    st.markdown("---")

    uploaded_file = st.file_uploader("📂 Kéo thả hoặc chọn file CSV", type="csv")
    
    if uploaded_file is not None:
        try:
            preview_df = pd.read_csv(uploaded_file, encoding='utf-8')
        except UnicodeDecodeError:
            try:
                uploaded_file.seek(0)
                preview_df = pd.read_csv(uploaded_file, encoding='latin-1')
            except UnicodeDecodeError:
                uploaded_file.seek(0)
                preview_df = pd.read_csv(uploaded_file, encoding='cp1252')

        st.write(f"**🔍 Xem trước dữ liệu tải lên ({len(preview_df)} sinh viên):**")
        st.dataframe(preview_df.head(5), use_container_width=True)
        
        if st.button("🔮 Bắt Đầu Phân Tích & Lưu Dữ Liệu", use_container_width=True):
            with st.spinner("Đang gửi dữ liệu tới máy chủ AI..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
                    current_user_id = st.session_state.user_data.get('id')
                    
                    response = requests.post(f"http://127.0.0.1:8000/api/upload-predict?user_id={current_user_id}", files=files)
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✅ {result['message']}")
                        
                        if 'admin_data' in st.session_state:
                            del st.session_state.admin_data
                            
                        st.info("Chuyển sang tab 'Thống kê hệ thống' để xem kết quả mô hình phân tích.")
                        st.balloons()
                    else:
                        error_detail = response.json().get('detail', 'Lỗi không xác định')
                        st.error(f"❌ Lỗi từ Backend: {error_detail}")
                        
                except Exception as e:
                    st.error(f"⚠️ Không thể kết nối tới Backend: {str(e)}")