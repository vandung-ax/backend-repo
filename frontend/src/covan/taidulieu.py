import streamlit as st
import pandas as pd
import requests

def inject_custom_css():
    st.markdown("""
    <style>
        .stApp { background-color: #f4f6f9; }
        .main-header { background-color: #154c8a; color: white; padding: 15px 20px; font-size: 22px; font-weight: bold; border-radius: 5px; margin-bottom: 20px; text-transform: uppercase; letter-spacing: 1px;}
        .page-title { color: #333; font-size: 20px; font-weight: bold; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

def show_upload_data():
    inject_custom_css()
    st.markdown('<div class="main-header">HỆ THỐNG CẢNH BÁO RỦI RO HỌC TẬP</div>', unsafe_allow_html=True)
    
    teacher_name = st.session_state.user_data.get('display_name', 'Giảng viên')
    st.markdown(f'<div class="page-title">👋 Chào mừng, {teacher_name} - 📤 Tải Dữ Liệu Mới & Dự Báo AI</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Hướng dẫn người dùng
    st.info("💡 Lưu ý: File CSV cần có ít nhất các cột: student_id, name và 11 cột đặc trưng mà AI yêu cầu.")

    file = st.file_uploader("Chọn tệp CSV từ máy tính", type="csv")

    if file is not None:
        # Đọc tạm để người dùng xem trước dữ liệu (fallback encoding để tránh UnicodeDecodeError)
        try:
            preview_df = pd.read_csv(file, encoding='utf-8')
        except UnicodeDecodeError:
            try:
                file.seek(0)
                preview_df = pd.read_csv(file, encoding='latin-1')
            except UnicodeDecodeError:
                file.seek(0)
                preview_df = pd.read_csv(file, encoding='cp1252')

        st.write("🔍 Xem trước dữ liệu tải lên:")
        st.dataframe(preview_df.head(5))
        
        # Nút bấm để kích hoạt AI Backend
        if st.button("🚀 Gửi dữ liệu & Dự đoán với CatBoost"):
            with st.spinner('Đang gửi dữ liệu tới máy chủ AI...'):
                try:
                    # Chuẩn bị file để gửi qua POST request
                    files = {"file": (file.name, file.getvalue(), "text/csv")}
                    current_user_id = st.session_state.user_data.get('id')
                    # Gửi tới endpoint /upload-predict trong predict.py của Backend
                    response = requests.post(f"http://127.0.0.1:8000/api/upload-predict?user_id={current_user_id}", files=files)
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✅ {result['message']}")
                        
                        # QUAN TRỌNG: Xóa dữ liệu cũ trong session để ép app tải lại dữ liệu mới từ Database
                        if 'admin_data' in st.session_state:
                            del st.session_state.admin_data
                        
                        st.info("Vui lòng chuyển sang trang 'Tổng quan' hoặc 'Thống kê' để xem kết quả mới nhất.")
                        st.balloons()
                    else:
                        error_detail = response.json().get('detail', 'Lỗi không xác định')
                        st.error(f"Lỗi từ Backend:! {error_detail}")
                    
                except Exception as e:
                 st.error(f"Không thể kết nối tới Backend:! {str(e)}")