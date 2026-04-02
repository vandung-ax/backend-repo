# pages/sinhviennguycocao.py
import streamlit as st
import pandas as pd
from utils import fetch_real_data
import json

def inject_custom_css():
    st.markdown("""
    <style>
        .stApp { background-color: #f4f6f9; }
        .main-header { background-color: #154c8a; color: white; padding: 15px 20px; font-size: 22px; font-weight: bold; border-radius: 5px; margin-bottom: 20px; text-transform: uppercase; letter-spacing: 1px;}
        .page-title { color: #333; font-size: 20px; font-weight: bold; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

def show_at_risk_students():
    inject_custom_css()
    st.markdown('<div class="main-header">HỆ THỐNG CẢNH BÁO RỦI RO HỌC TẬP</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">⚠️ Sinh Viên Nguy Cơ Cao Theo Lớp</div>', unsafe_allow_html=True)
    st.markdown("---")

    data = fetch_real_data(scope="assigned")

    if data:
        df_all = pd.DataFrame(data)
        df_all['created_at'] = pd.to_datetime(df_all['created_at'])
        latest_batch = df_all['created_at'].max()
        
        at_risk_df = df_all[(df_all['risk_score'] >= 0.65) & (df_all['created_at'] == latest_batch)]

        if at_risk_df.empty:
            st.success("Không có sinh viên nguy cơ cao trong đợt dự báo này.")
        else:
            list_lop = at_risk_df['Lop'].unique()
            
            # --- TẠO TABS CHO TỪNG LỚP ---
            tabs = st.tabs([f"🏫 Lớp {lop}" for lop in list_lop])
            
            for i, lop in enumerate(list_lop):
                with tabs[i]:
                    df_lop = at_risk_df[at_risk_df['Lop'] == lop]
                    st.info(f"Phát hiện **{len(df_lop)}** sinh viên có rủi ro cao trong lớp này.")
                    
                    for index, s in df_lop.iterrows():
                        # --- TẠO EXPANDER CHO TỪNG SINH VIÊN ---
                        with st.expander(f"🔴 {s['MSSV']} - {s['HoTen']} | Rủi ro: {s['risk_score']*100:.1f}%"):
                            
                            st.write("**📊 Chi tiết 11 chỉ số học tập**")
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

                            # Lý do
                            reasons = s.get('reasons', [])
                            if reasons:
                                st.write("**🚩 Lý do dẫn đến cảnh báo**")
                                try:
                                    res_list = json.loads(reasons) if isinstance(reasons, str) else reasons
                                    if isinstance(res_list, list):
                                        for r in res_list: st.info(f"📍 {r}")
                                    else:
                                        st.info(f"📍 {res_list}")
                                except Exception:
                                    st.info(f"📍 {reasons}")
                            
                            # Câu chuyện AI
                            ai_path = s.get('ai_explanation_path')
                            if pd.notna(ai_path) and ai_path:
                                st.write("**🕵️‍♂️ Phân tích kỹ thuật (Câu chuyện suy luận của AI)**")
                                try:
                                    path_list = json.loads(ai_path) if isinstance(ai_path, str) else ai_path
                                    if isinstance(path_list, list) and len(path_list) > 0:
                                        formatted_text = ""
                                        for line in path_list:
                                            cleaned_line = line.strip(' "')
                                            if "Xét [" in cleaned_line:
                                                formatted_text += f"**{cleaned_line}**\n\n"
                                            elif "==> DỰ ĐOÁN CUỐI CÙNG" in cleaned_line:
                                                formatted_text += f"❌ :red-background[{cleaned_line}]\n\n"
                                            else:
                                                formatted_text += f"{cleaned_line}\n\n"
                                        st.markdown(formatted_text)
                                except Exception:
                                    pass
                            
                            # --- LOGIC XỬ LÝ NÚT AI TƯ VẤN MỚI ---
                            saved_advices = s.get('advices', [])
                            advice_key = f"advice_{s['MSSV']}"
                            
                            # 1. Ưu tiên 1: Đã có trong Database -> In ra luôn, KHÔNG HIỆN NÚT BẤM
                            if saved_advices and len(saved_advices) > 0:
                                st.markdown("### 🤖 Cố vấn AI Đề xuất (Đã lưu)")
                                for idx, adv in enumerate(saved_advices):
                                    st.success(f"**Lời khuyên {idx + 1}:**\n\n{adv}")
                                    
                            # 2. Ưu tiên 2: Vừa tạo xong (nằm trong session state) -> Hiện ra
                            elif advice_key in st.session_state:
                                st.markdown("### 🤖 Cố vấn AI Đề xuất (Mới tạo)")
                                st.success(st.session_state[advice_key])
                                
                            # 3. Ưu tiên 3: Chưa có dữ liệu -> Mới vẽ nút bấm ra
                            else:
                                if st.button(f"🤖 Nhận lời khuyên cho {s['MSSV']}", key=f"btn_{s['MSSV']}"):
                                    with st.spinner("Đang phân tích và lưu vào cơ sở dữ liệu..."):
                                        from utils import fetch_or_generate_advice
                                        st.session_state[advice_key] = fetch_or_generate_advice(s['MSSV'])
                                        st.rerun()

    else:
        st.info("Chưa có dữ liệu dự báo. Vui lòng tải dữ liệu lên.")