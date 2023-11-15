import cv2
import numpy as np
from google.cloud import vision
from google.oauth2 import service_account
import io
import base64

# 구글 키 파일 경로 설정
credentials_path = 'inbound-bee-234915-0490831a85a5.json'

# 구글 서비스 계정 인증 설정
credentials = service_account.Credentials.from_service_account_file(credentials_path)
client = vision.ImageAnnotatorClient(credentials=credentials)

# 파일 주소
scanned_png = './시험지/SampleData/MCQ/T2/Scanned/converted_62.png'
templateMatching_png = './시험지/SampleData/student_template/studentName.png'

# 이미지를 읽어온다
img_array = np.fromfile(scanned_png, np.uint8)
scanned_png = cv2.imdecode(img_array,cv2.IMREAD_GRAYSCALE)


img_array = np.fromfile(templateMatching_png, np.uint8)
templateMatching_png = cv2.imdecode(img_array,cv2.IMREAD_GRAYSCALE)

def find_multiple_occurrences(scanned_png, templateMatching_png, threshold=0.8):
    
    # 템플릿 매칭을 수행합니다.
    result = cv2.matchTemplate(scanned_png, templateMatching_png, cv2.TM_CCOEFF_NORMED)

    # 매칭 결과에서 임계값 이상인 위치 찾기.
    locations = np.where(result >= threshold)

    occurrences = []
    for loc in zip(*locations[::-1]):
        occurrences.append(loc)

    return occurrences

# templateMatching_png의 여러 위치 찾기
occurrences = find_multiple_occurrences(scanned_png, templateMatching_png)
w, h = templateMatching_png.shape[::-1]

# 찾은 위치를 scanned_png에 표시
for pt in occurrences:
    x1, y1 = pt
    x2, y2 = (x1 + w, y1 + h)
    cv2.rectangle(scanned_png, (x1, y1), (x2, y2), (0, 255, 0), 1)

# 이름/학번 영역
for pt in occurrences:
    x1, y1 = pt
    x2, y2 = (x1 + w, y1 + h)

    # 이름 영역
    Name_x1 = x1 + 160
    Name_y1 = y1 - 20
    
    Name_x2 = x2 + 500
    Name_y2 = y2 + 20

    #학번 영역
    Number_x1 = x1 + 160
    Number_y1 = y1 + 70
    
    Number_x2 = x2 + 500
    Number_y2 = y2 + 140

Name_png = scanned_png[Name_y1:Name_y2, Name_x1:Name_x2]
#ret, Name_png = cv2.threshold(Name_png, 127, 255, cv2.THRESH_BINARY_INV)
cv2.imshow('Name_png', Name_png)

Number_png = scanned_png[Number_y1:Number_y2, Number_x1:Number_x2]
#ret, Number_png = cv2.threshold(Number_png, 127, 255, cv2.THRESH_BINARY_INV)
cv2.imshow('Number_png', Number_png)


# api로 보낼 이미지 리스트
cropped_images = []

cropped_images.append(Name_png)
cropped_images.append(Number_png)

ii = 0

for cropped_image in cropped_images :
    # crop된 이미지를 인코딩 및 변환
    cv2.imwrite(f"./build/{ii}.jpg",cropped_image)
    ii+=1
    _, encoded_image = cv2.imencode('.png', cropped_image)
    image_content = base64.b64encode(encoded_image.tobytes()).decode('utf-8')

    # Vision API에 이미지 전송하여 텍스트 추출
    image = vision.Image(content=image_content)
    response = client.document_text_detection(image=image, image_context={"language_hints": ["ko"]})
    print(response.full_text_annotation.text)


cv2.waitKey(0)
cv2.destroyAllWindows()