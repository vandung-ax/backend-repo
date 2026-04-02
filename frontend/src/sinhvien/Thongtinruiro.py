import streamlit as st
import pandas as pd
from utils import fetch_real_data
import json

def show_risk_analysis(mssv):
    st.subheader("🔍 Phân tích rủi ro cá nhân")
    st.markdown("---")

    # Gọi API lấy dữ liệu thực
    data = fetch_real_data()

    if data:
        df_all = pd.DataFrame(data)
        
        # Đảm bảo trường created_at là datetime để so sánh
        df_all['created_at'] = pd.to_datetime(df_all['created_at'])
        
        # Lấy đợt dự báo mới nhất
        latest_batch = df_all['created_at'].max()
        
        # LỌC: Chỉ lấy dữ liệu của sinh viên đang đăng nhập (mssv) ở đợt mới nhất
        student_df = df_all[(df_all['MSSV'] == str(mssv)) & (df_all['created_at'] == latest_batch)]

        if student_df.empty:
            st.success("🎉 Xin chúc mừng! Bạn không nằm trong danh sách cảnh báo rủi ro ở đợt dự báo mới nhất.")
        else:
            # Vì mỗi sinh viên chỉ có 1 bản ghi trong 1 đợt, ta lấy dòng đầu tiên
            s = student_df.iloc[0]
            
            st.error(f"⚠️ Mức độ rủi ro hiện tại của bạn: **{s['risk_score']*100:.1f}%**")
            
            # 1. HIỂN THỊ 11 THUỘC TÍNH
            st.markdown("### 📊 Chi tiết 11 chỉ số học tập")
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.write(f"• Chuyên cần: **{s.get('attendance', 0)}%**")
                st.write(f"• Giờ học: **{s.get('hours_studied', 0)}h**")
                st.write(f"• Điểm cũ: **{s.get('previous_scores', 0)}**")
            with c2:
                st.write(f"• Tài liệu: **{s.get('access_to_resources', 'N/A')}**")
                st.write(f"• Động lực: **{s.get('motivation_level', 'N/A')}**")
                st.write(f"• Thu nhập: **{s.get('family_income', 'N/A')}**")
            with c3:
                st.write(f"• Giờ ngủ: **{s.get('sleep_hours', 0)}h**")
                st.write(f"• Bạn bè: **{s.get('peer_influence', 'N/A')}**")
                st.write(f"• Ngoại khóa: **{s.get('extracurricular_activities', 'N/A')}**")
            with c4:
                st.write(f"• Khoảng cách: **{s.get('distance_from_home', 'N/A')}**")
                st.write(f"• Giáo viên: **{s.get('teacher_quality', 'N/A')}**")

            st.divider()

            # 2. HIỂN THỊ LÝ DO (Đã bỏ toàn bộ code liên quan đến AI Advice)
            reasons = s.get('reasons', [])
            st.markdown("### 🚩 Lý do dẫn đến cảnh báo")
            if reasons:
                try:
                    res_list = json.loads(reasons) if isinstance(reasons, str) else reasons
                    if isinstance(res_list, list):
                        for r in res_list: 
                            st.info(f"📍 {r}")
                    else:
                        st.info(f"📍 {res_list}")
                except Exception:
                    st.info(f"📍 {reasons}")
            else:
                st.warning("Không có dữ liệu lý do rủi ro.")
                
    else:
        st.info("Chưa có dữ liệu dự báo. Vui lòng đợi quản trị viên cập nhật hệ thống.")