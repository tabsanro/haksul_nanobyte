import base64
import openai
import os
import speech_recognition as sr
import psycopg2
from sentence_transformers import SentenceTransformer, util

openai.api_key = "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"

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Function to capture voice command and convert to text
def get_voice_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something...")
        audio = recognizer.listen(source)

    try:
        # Recognize speech using Google Web Speech API
        return recognizer.recognize_google(audio, language="ko-KR") # audio 가 음성파일?
    except sr.UnknownValueError:
        print("Could not understand audio")
        return ""
    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))
        return ""

# PostgreSQL 데이터베이스 연결 및 데이터 가져오기
def connect_db():
    connection = psycopg2.connect(
        host="localhost",   # 실제 데이터베이스 호스트로 변경
        user="myuser",    # 실제 데이터베이스 사용자 이름으로 변경
        password="1234", # 실제 비밀번호로 변경
        dbname="mydb"
    )
    return connection

def fetch_all_items():
    connection = connect_db()
    cursor = connection.cursor()
    cursor.execute("SELECT product_name, price, image FROM product")
    items = cursor.fetchall()
    cursor.close()
    connection.close()
    return items

items = fetch_all_items() # -> 
all_items_text = "\n".join([f"물품 이름: {item[0]}, 가격: {item[1]}, 이미지 URL: {item[2]}" for item in items])

# 기본 텍스트와 음성 명령 입력
# user_response = "내가 해외여행을 갈건데 뭘 챙길까?"  # 빈 문자열로 초기화 가능
user_response = "이럴땐 어떻게 해?"
# user_response가 빈 경우에만 음성 입력을 받음
if not user_response:
    user_response = get_voice_command()

# Path to your image
# image_path = "./asdf/test.png"
image_path = "test.png"

def is_image_file(image_path):
    # Check if the file exists
    if not os.path.isfile(image_path):
        return False
    
    # Check if the file has a common image extension
    valid_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"}
    _, ext = os.path.splitext(image_path)
    return ext.lower() in valid_extensions

if is_image_file(image_path):
    # 이미지가 존재하는 경우 실행할 코드
    print("Image file exists and is valid.")
    base64_image = encode_image(image_path) # 이미지를 base64로 인코딩
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "너는 상황에 따라서 물품을 추천하는 AI야. 가령, 집에 바퀴벌레가 나오면 살충제를 추천해주고 금이 간 벽이 있으면 보수 테이프 같은걸 추천해주면 돼. 데이터베이스를 연결해서 알려줄건데, 물품명을 최대 3개까지만 출력해줘. 반드시 물품명만을 출력해야되고, 쉼표로 구분하면 돼. 예를들어 보수테이프, 방수테이프, 레진 이런 느낌으로 출력하고 가장 연관성이 높은 순서대로 출력해줘. 그리고 맨 처음에는 사용자의 상황을 한줄로 요약해서 한 문장으로만 출력해줘. 그니깐 사용자가 배가 고파 하면 '배가 고픈 상황입니다. 빵, 케이크, 사탕' 이런 식으로 출력해줘! 반드시 맨 처음에 상황을 요약하는 한 문장과 뒤에 최대 3가지 물품을 출력해야해! 그리고 반드시 데이터베이스 안에 있는 물품만 말해줘 적합한게 없으면 딱 한개만이라도 말해줘" \
                            + all_items_text + user_response,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        },
                    },
                ],
            }
        ],
    )

else:
    # 이미지가 존재하지 않는 경우 실행할 코드
    print("Image file does not exist or is not a valid image.")
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "너는 상황에 따라서 물품을 추천하는 AI야. \
             가령, 집에 바퀴벌레가 나오면 살충제를 추천해주고 금이 간 벽이 있으면 보수 테이프 같은걸 추천해주면 돼. \
             데이터베이스를 연결해서 알려줄건데, 물품명을 최대 3개까지만 출력해줘. 반드시 물품명만을 출력해야되고, 쉼표로 구분하면 돼. \
             예를들어 보수테이프, 방수테이프, 레진 이런 느낌으로 출력하고 가장 연관성이 높은 순서대로 출력해줘. \
             그리고 맨 처음에는 사용자의 상황을 한줄로 요약해서 한 문장으로만 출력해줘. 그니깐 사용자가 배가 고파 하면 '배가 고픈 상황입니다. \
             빵, 케이크, 사탕' 이런 식으로 출력해줘! 반드시 맨 처음에 상황을 요약하는 한 문장과 뒤에 3가지 물품을 출력해야해!" 
             + all_items_text},
            {"role": "user", "content": user_response}
        ]
    )

print(response.choices[0].message["content"])
