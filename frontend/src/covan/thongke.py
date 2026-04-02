import streamlit as st
import pandas as pd
import altair as alt
from utils import fetch_all_student_data

def inject_custom_css():
    st.markdown("""
    <style>
        .stApp { background-color: #f4f6f9; }
        .main-header { background-color: #154c8a; color: white; padding: 15px 20px; font-size: 22px; font-weight: bold; border-radius: 5px; margin-bottom: 20px; text-transform: uppercase; letter-spacing: 1px;}
        .page-title { color: #333; font-size: 20px; font-weight: bold; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

def draw_bar_chart(data, x_col, y_col, title, is_risk_level=False):
    """Hàm vẽ biểu đồ bar đồng nhất cho tất cả các chỉ số"""
    # Danh sách sắp xếp chuẩn từ Database
    order_list = ['THẤP (An toàn)', 'TRUNG BÌNH (Cảnh báo)', 'CAO (Nguy hiểm)']
    
    x_axis = alt.X(x_col, axis=alt.Axis(labelAngle=0), title=None)
    if is_risk_level:
        x_axis = alt.X(x_col, sort=order_list, axis=alt.Axis(labelAngle=0), title=None)
        
    chart = alt.Chart(data).mark_bar().encode(
        x=x_axis,
        y=alt.Y(y_col, title=None),
        color=alt.value('#1f77b4') # Tất cả xanh hết
    ).properties(height=250)
    
    st.write(f"**{title}**")
    st.altair_chart(chart, use_container_width=True)

def show_statistics():
    inject_custom_css()
    st.markdown('<div class="main-header">HỆ THỐNG CẢNH BÁO RỦI RO HỌC TẬP</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">📈 Thống Kê Hệ Thống Dự Báo Rủi Ro</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    df = fetch_all_student_data()

    if not df.empty:
        df['created_at'] = pd.to_datetime(df['created_at'])
        df_latest = df[df['created_at'] == df['created_at'].max()].copy()
        
        # --- NHÓM 1: CHỈ SỐ ĐỊNH LƯỢNG (Bảng risk_features + risk_thresholds) ---
        st.write("### 📊 Chỉ số học tập TB theo Mức rủi ro")
        
        # ==========================================
        # HÀNG 1
        # ==========================================
        r1_c1, r1_c2 = st.columns(2)

        with r1_c1:
            # Chuyên cần
            d_att = df_latest.groupby('risk_level')['attendance'].mean().reset_index()
            draw_bar_chart(d_att, 'risk_level', 'attendance', "Chuyên cần TB (%)", is_risk_level=True)

        with r1_c2:
            # Điểm số
            st.write("**Phân bố Điểm số cũ (Tăng dần)**")
            # Thêm height=250 để đồng bộ chiều cao với biểu đồ cột
            st.line_chart(df_latest['previous_scores'].sort_values().reset_index(drop=True), height=250)
            
        st.write("") # Tạo khoảng trống nhỏ giữa 2 hàng

        # ==========================================
        # HÀNG 2
        # ==========================================
        r2_c1, r2_c2 = st.columns(2)
        
        with r2_c1:
            # Giờ học
            d_hours = df_latest.groupby('risk_level')['hours_studied'].mean().reset_index()
            draw_bar_chart(d_hours, 'risk_level', 'hours_studied', "Giờ học TB (Giờ)", is_risk_level=True)
            
        with r2_c2:
            # Giờ ngủ (Thay thế vị trí để lấp đầy grid 2x2)
            d_sleep = df_latest.groupby('risk_level')['sleep_hours'].mean().reset_index()
            draw_bar_chart(d_sleep, 'risk_level', 'sleep_hours', "Giờ ngủ TB (Giờ)", is_risk_level=True)

        st.divider()
        
        # --- NHÓM 2: CÁC YẾU TỐ ĐỊNH DANH (Bảng risk_features) ---
        # (Phần này giữ nguyên hoàn toàn như cũ)
        st.write("### 📋 Phân bổ các yếu tố tác động khác")
        c1, c2, c3 = st.columns(3)

        with c1:
            draw_bar_chart(df_latest['motivation_level'].value_counts().reset_index(), 'motivation_level', 'count', "Mức độ Động lực")
            draw_bar_chart(df_latest['family_income'].value_counts().reset_index(), 'family_income', 'count', "Thu nhập Gia đình")

        with c2:
            draw_bar_chart(df_latest['access_to_resources'].value_counts().reset_index(), 'access_to_resources', 'count', "Tài nguyên học tập")
            draw_bar_chart(df_latest['peer_influence'].value_counts().reset_index(), 'peer_influence', 'count', "Ảnh hưởng Bạn bè")

        with c3:
            draw_bar_chart(df_latest['teacher_quality'].value_counts().reset_index(), 'teacher_quality', 'count', "Chất lượng GV")
            draw_bar_chart(df_latest['extracurricular_activities'].value_counts().reset_index(), 'extracurricular_activities', 'count', "Ngoại khóa")

    else:
        st.warning("Hiện chưa có dữ liệu thống kê.")