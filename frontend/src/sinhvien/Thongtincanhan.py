import streamlit as st
import requests

def show_personal_info(mssv):
    st.subheader("📋 Thông Tin Cá Nhân")
    st.markdown("---")
    
    try:
        # Gọi API lấy dữ liệu thực từ Backend
        response = requests.get(f"http://localhost:8000/api/student/{mssv}")
        
        if response.status_code == 200:
            data = response.json()
            
            st.markdown("### 🎓 Hồ sơ định danh")
            
            # Chia làm 2 cột để căn chỉnh thông tin đẹp mắt
            with st.container():
                col1, col2 = st.columns(2)
                
                with col1:
                    st.info(f"🆔 **Mã số sinh viên (MSSV):** \n\n ### {data['MSSV']}")
                    st.success(f"👤 **Họ và tên:** \n\n ### {data['HoTen']}")
                    
                with col2:
                    st.warning(f"📚 **Ngành học:** \n\n ### {data['Nganh']}")
                    # Dùng chung st.info với MSSV để tạo sự cân bằng về màu sắc
                    st.info(f"🏢 **Trực thuộc Khoa:** \n\n ### {data['TenKhoa']}")
                    
        else:
            st.error("Không thể tải thông tin sinh viên từ máy chủ.")
            
    except Exception as e:
        st.error(f"⚠️ Lỗi kết nối: {e}")