import base64
import requests
import streamlit as st
import json

# OpenAI API Key
api_key = st.secrets["api_key"] # 4월 5일 김채원 수정

st.title("ChatGPT 과일 당뇨 지수 계산기")

# generated from Chat GPT
# Function to encode the image
def encode_image(image):
    return base64.b64encode(image).decode('utf-8')

def load_data(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data
    
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
                        "text": "Let me know the GI index of the food in the photo I just posted. The format is korean_food_name = GI number, You MUST give me Korean food name!. and display all results vertically, please. And all words other than this answer are omitted. And if there's no result, just answer 'none' in English"
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
      
        # Show loading spinner while analyzing image
        with st.spinner('분석 중입니다...'):
            # Analyze image
            result = analyze_image(picture)

        # JSON 파일 경로
        file_path = "fruit_data.json"
        
        # JSON 파일 로드
        fruit_data = load_data(file_path)
    
        # 데이터 출력
        #st.write("Loaded Data:", fruit_data)

        if result == "none" or result == "없음":
            st.write("과일을 인식할 수 없습니다. 다시 시도해주시겠어요?")
        else:
            # 분석 결과 표시
            st.write("### 과일 분석 결과")

            # 각 줄을 분할하여 처리
            for line in result.split('\n'):
                # '=' 기준으로 문자열을 두 부분으로 분리
                parts = line.split('=')
                if len(parts) == 2:
                    name = parts[0].strip()
                    number_gpt = int(parts[1].strip())
                    number_json = 0
                    GI_number = number_gpt
                    #st.write("Korean Fruit Name:", name)
                    #st.write("GI Number:", GI_number)
                    # 만약 해당 과일 이름이 JSON 데이터에 있다면 해당 GI 값을 반환
                    if name in fruit_data["fruit_gi"]:
                        number_json = fruit_data["fruit_gi"][name]
                    
                    st.write("과일 이름 :", name)
                    if number_json != 0:
                        st.write("GI (JSON) :", number_json)
                        GI_number = number_json
                    else:
                        st.write("GI (GPT) :", number_gpt)

                    # gi_level 배열에서 현재 GI 수치가 속하는 단계 확인
                    gi_levels = fruit_data["gi_level"]
                    level = 0  # 기본값은 낮음
                    
                    for idx, gi_threshold in enumerate(gi_levels):
                        if GI_number < gi_threshold:
                            level = idx
                            break

                    # level에 따라서 낮음, 보통, 높음 출력
                    if level == 0:
                        st.write(f"{name}의 GI 지수 ({GI_number})는 낮음입니다.")
                    elif level == 1:
                        st.write(f"{name}의 GI 지수 ({GI_number})는 보통입니다.")
                    else:
                        st.write(f"{name}의 GI 지수 ({GI_number})는 높음입니다.")
                        
if __name__ == "__main__":
    main()
