import streamlit as st
import pandas as pd
import json 
from PIL import Image
from utils import fetch_all_student_data, fetch_train_history, fetch_dashboard_stats

def show_statistics():
    st.markdown("""
    <style>
        .main-header { background-color: #154c8a; color: white; padding: 15px 20px; font-size: 22px; font-weight: bold; border-radius: 5px; margin-bottom: 20px;}
        .result-card { background-color: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #e1e4e8; border-top: 5px solid #28a745; margin-top: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        .metric-card { background-color: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center; border: 1px solid #dee2e6; box-shadow: 0 2px 4px rgba(0,0,0,0.05);}
        .metric-title { font-size: 18px; font-weight: bold; color: #495057; margin-bottom: 10px;}
        .metric-value { font-size: 36px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="main-header">TỔNG QUAN VỀ HỆ THỐNG VÀ MÔ HÌNH AI</div>', unsafe_allow_html=True)

    # ==========================================
    # 1. TRANG THỐNG KÊ ĐẦU TIÊN: TỔNG SỐ LƯỢNG
    # ==========================================
    st.markdown("### 👥 Số liệu Hệ thống")
    stats = fetch_dashboard_stats()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">👨‍🎓 Sinh viên</div>
            <div class="metric-value" style="color: #154c8a;">{stats['total_sinhvien']}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">👨‍🏫 Cố vấn học tập</div>
            <div class="metric-value" style="color: #28a745;">{stats['total_covan']}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">🔑 Tài khoản</div>
            <div class="metric-value" style="color: #ffc107;">{stats['total_taikhoan']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><hr>", unsafe_allow_html=True)

    # ==========================================
    # 2. HIỆN HÌNH ẢNH MÔ HÌNH ĐÁNH GIÁ
    # ==========================================
    st.markdown("### 📈 Hiệu suất mô hình AI (CatBoost)")
    try:
        image = Image.open('src/admin/anh.png')
        st.image(image, caption='Ma trận nhầm lẫn (Confusion Matrix) & Biểu đồ ROC-AUC', use_container_width=True)
    except FileNotFoundError:
        st.warning("⚠️ Không tìm thấy file hình ảnh 'src/admin/anh.png'. Vui lòng kiểm tra lại đường dẫn.")

    st.markdown("<br><hr>", unsafe_allow_html=True)

    # ==========================================
    # 3. CUỐI CÙNG BÊN DƯỚI LÀ CÂY QUYẾT ĐỊNH
    # ==========================================
    st.markdown("### 🌲 Lịch sử các phiên bản Cây quyết định")
    history_data = fetch_train_history()
    
    if not history_data:
        st.info("Chưa có phiên bản huấn luyện nào được lưu. Vui lòng Huấn luyện và Đồng bộ cây bên trang 'Huấn luyện AI'.")
    else:
        # Lặp qua để hiện danh sách các cây, mới nhất nằm trên cùng
        for item in history_data:
            with st.expander(f"🟢 Phiên bản {item['version']} - Đồng bộ lúc: {item['created_at']}"):
                st.write("**Thông số & Cấu trúc cây mới nhất:**")
                st.json(item['tree_rules'])

    st.markdown("<br><hr>", unsafe_allow_html=True)

    # ==========================================
    # 4. PHẦN BIỂU ĐỒ SINH VIÊN (Tuỳ chọn bổ sung nếu có)
    # ==========================================
    data = fetch_all_student_data()
    if data.empty:
        st.info("Chưa có dữ liệu chi tiết của sinh viên để vẽ biểu đồ phân tích sâu.")
        return
        
    # (Nếu bạn có code vẽ biểu đồ matplotlib/plotly ở file cũ, bạn dán nối tiếp vào đây nhé)