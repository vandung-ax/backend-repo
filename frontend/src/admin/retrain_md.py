import streamlit as st
import pandas as pd
import requests
import time
from utils import sync_tree_from_ai 

def show_retrain_system():
    st.markdown("""
    <style>
        .main-header { background-color: #154c8a; color: white; padding: 15px 20px; font-size: 22px; font-weight: bold; border-radius: 5px; margin-bottom: 20px;}
        .page-title { color: #333; font-size: 20px; font-weight: bold; margin-bottom: 5px; }
        .info-box { background-color: #e7f3ff; padding: 15px; border-radius: 8px; border: 1px solid #b3d7ff; color: #004085; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-header">HUẤN LUYỆN LẠI MÔ HÌNH AI</div>', unsafe_allow_html=True)
    
    admin_name = st.session_state.user_data.get('display_name', 'Quản trị viên')
    current_user_id = st.session_state.user_data.get('id')

    # Chia layout làm 2 cột
    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.markdown(f'<div class="page-title">1. Gửi dữ liệu huấn luyện</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("📂 Chọn file dữ liệu (.csv)", type="csv", key="retrain_upload_csv")
        
        if uploaded_file is not None:
            if st.button("🚀 BẮT ĐẦU HUẤN LUYỆN LẠI", use_container_width=True, type="primary"):
                with st.spinner("🤖 Đang gửi yêu cầu tới máy chủ AI..."):
                    try:
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
                        response = requests.post(f"http://127.0.0.1:8000/api/retrain-model?user_id={current_user_id}", files=files)
                        
                        if response.status_code == 200:
                            result = response.json()
                            msg = result.get('message', 'Đang xử lý ngầm.')
                            st.success("✅ Gửi yêu cầu thành công!")
                            st.markdown(f"""
                            <div class="info-box">
                                <b>📢 Phản hồi từ AI:</b> {msg}<br><br>
                                ⏳ <b>Vui lòng chờ khoảng 2-3 phút</b> để quá trình học hoàn tất. Sau đó nhấn nút Đồng bộ bên cạnh.
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.error(f"❌ Lỗi: {response.text}")
                    except Exception as e:
                        st.error(f"⚠️ Lỗi kết nối: {str(e)}")

    with col2:
        st.markdown(f'<div class="page-title">2. Đồng bộ kết quả</div>', unsafe_allow_html=True)
        st.info("Nhấn nút bên dưới ĐỂ LẤY CÂY MỚI NHẤT sau khi AI đã học xong (Chờ ~3 phút sau khi bấm Train).")
        
        if st.button("🔄 ĐỒNG BỘ CÂY QUYẾT ĐỊNH MỚI", use_container_width=True):
            with st.spinner("Đang kết nối để tải cây mới..."):
                success, msg = sync_tree_from_ai(current_user_id)
                if success:
                    st.success(f"✅ {msg}")
                    st.balloons()
                    time.sleep(1.5)
                    st.info("💡 Bạn có thể xem kết quả cây mới tại trang **Thống kê hệ thống**")
                else:
                    st.error(f"❌ Đồng bộ thất bại: {msg}")