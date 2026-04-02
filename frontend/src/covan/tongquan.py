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

def show_overview():
    inject_custom_css()
    st.markdown('<div class="main-header">HỆ THỐNG CẢNH BÁO RỦI RO HỌC TẬP</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">📊 Tổng Quan Hệ Thống Dự Báo</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Lấy dữ liệu đã gộp từ các bảng: sinhvien, khoa, risk_thresholds, risk_features
    df = fetch_all_student_data()

    if not df.empty:
        # Lọc đợt dự báo mới nhất dựa trên bảng risk_thresholds
        df['created_at'] = pd.to_datetime(df['created_at'])
        latest_time = df['created_at'].max()
        df_latest = df[df['created_at'] == latest_time].copy()
        
        # --- TÍNH TOÁN CHỈ SỐ (METRICS) ---
        total_sv = len(df_latest) # Từ bảng sinhvien
        avg_risk = df_latest['risk_score'].mean() * 100 # Từ bảng risk_thresholds
        high_risk = len(df_latest[df_latest['risk_score'] >= 0.65]) # Ngưỡng rủi ro cao
        avg_att = df_latest['attendance'].mean() # Từ bảng risk_features

        #st.write(f"### 📍 Dữ liệu đợt: {latest_time.strftime('%d/%m/%Y %H:%M')}")
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.metric("🎓 Tổng sinh viên thực hiện dự báo", f"{total_sv} SV")
        with m2: st.metric("📊 Tỷ lệ rủi ro TB", f"{avg_risk:.1f}%")
        with m3: st.metric("🚨 Số Sinh viên nguy cơ cao", f"{high_risk} SV")
        #with m4: st.metric("📈 Chuyên Cần TB", f"{avg_att:.1f}%")

        st.markdown("---")

        c1, c2 = st.columns(2)
        
        with c1:
            st.write("**Phân Bố Mức Độ Rủi Ro (Số lượng SV)**")
            risk_counts = df_latest['risk_level'].value_counts().reset_index()
            risk_counts.columns = ['Mức độ', 'Số lượng']
            
            # Thứ tự sắp xếp khớp với nhãn trong Database
            order_list = ['THẤP (An toàn)', 'TRUNG BÌNH (Cảnh báo)', 'CAO (Nguy hiểm)']
            
            chart_risk = alt.Chart(risk_counts).mark_bar().encode(
                x=alt.X('Mức độ', sort=order_list, axis=alt.Axis(labelAngle=0), title=None),
                y=alt.Y('Số lượng', title=None),
                color=alt.value('#1f77b4') # Màu xanh đồng nhất
            ).properties(height=300)
            st.altair_chart(chart_risk, use_container_width=True)

        with c2:
            st.write("**Phân Bố Điểm Rủi Ro (Toàn khoa %)**")
            risk_dist = (df_latest['risk_score'] * 100).sort_values().reset_index(drop=True)
            st.line_chart(risk_dist)
            
        st.divider()
        # Thống kê kết hợp bảng Khoa và bảng Risk Thresholds
      

    else:
        st.info("Chưa có dữ liệu dự báo trong database.")