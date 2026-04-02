import requests

AI_API_URL = "https://ai-student-api.onrender.com/api/predict"

def call_ai_prediction(student_data: dict):
    try:
        # Gửi 1 object duy nhất {} theo yêu cầu của Render
        response = requests.post(AI_API_URL, json=student_data, timeout=120)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Lỗi kết nối AI: {str(e)}")
        return None