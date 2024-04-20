import base64
import requests
import streamlit as st

# OpenAI API Key
api_key = st.secrets["api_key"] # 4월 5일 김채원 수정

st.title("ChatGPT 과일 당뇨 지수 체커")

# generated from Chat GPT
# Function to encode the image
def encode_image(image):
    return base64.b64encode(image).decode('utf-8')

def analyze_image(image_data):
    base64_image = encode_image(image_data)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Let me know the GI index of the fruit in the photo I just posted. The format is 'name=number', and all words other than this answer are omitted."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 1024
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    message_value = response.json()['choices'][0]['message']['content']
    return message_value

def main():
    # 사용자에게 옵션 제공
    option = st.radio("사진을 어떻게 제공하시겠습니까?", ("카메라로 찍기", "앨범에서 선택하기"))

    if option == "카메라로 찍기":
        # 카메라 입력 받기
        uploaded_file = st.camera_input("사진 촬영")
    else:
        # 앨범에서 이미지 선택
        uploaded_file = st.file_uploader("앨범에서 이미지 선택", type=["jpg", "jpeg"])

    if uploaded_file is not None:
        picture = uploaded_file.read()
    else:
        picture = None

    if picture is not None:
        st.image(picture)
        
        result = analyze_image(picture)
        
        # 분석 중 메시지 표시
        st.write("분석중...")
        
        # 분석 결과 표시
        st.write("### 과일 분석 결과")
        st.write(result)
        
if __name__ == "__main__":
    main()
