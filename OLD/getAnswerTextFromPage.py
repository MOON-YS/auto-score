#최유현 11.09. 20:00
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

# 이미지 load

image_a_path = './서술형1/converted_68.png' #이미지 경로 앞에 r은 읽어오는데 필요해서 붙임
template_b_path = 'arrow.png' #이미지 경로 앞에 r은 읽어오는데 필요해서 붙임

img_array = np.fromfile(image_a_path, np.uint8)
image_a = cv2.imdecode(img_array,cv2.IMREAD_COLOR)

img_array = np.fromfile(template_b_path, np.uint8)
template_b = cv2.imdecode(img_array,cv2.IMREAD_GRAYSCALE)
template_b = cv2.cvtColor(template_b, cv2.COLOR_GRAY2BGR)

# api로 보낼 이미지 리스트
cropped_images = []

def find_multiple_occurrences(image_a, template_b, threshold=0.65):
    result = cv2.matchTemplate(image_a, template_b, cv2.TM_CCOEFF_NORMED)
    
    locations = np.where(result >= threshold)
    
    occurrences = []
    for loc in zip(*locations[::-1]):
        occurrences.append((loc, (loc[0] + template_b.shape[1], loc[1] + template_b.shape[0])))
    
    return occurrences

occurrences = find_multiple_occurrences(image_a, template_b)

# RGB그림을 그레이스케일로 변경    
gray = cv2.cvtColor(image_a, cv2.COLOR_BGR2GRAY)

# 코너 검출
edges = cv2.Canny(gray, 50, 150)

# 윤곽선 검출 함수
contours, _ = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 사각형 넓이가 일정이상일때, 이미지에서 검출
rectangles = [cnt for cnt in contours if cv2.contourArea(cnt) > 1]

# 화살표의 중심좌표가 사각형의 범위안에 있는 경우의 사각형만 인식
for i, cnt in enumerate(rectangles):
    for (start, end) in occurrences:
        center_x = start[0] + (end[0] - start[0]) // 2  
        center_y = start[1] + (end[1] - start[1]) // 2  
        x, y, w, h = cv2.boundingRect(cnt)
        x_min = x - w/2
        x_max = x + w/2
        y_min = y - h/2
        y_max = y + h/2

        if x <= center_x <= x + w and y <= center_y <= y + h:
            cropped_images.append(image_a[y:y+h, x:x+w])

print(len(cropped_images))
ii = 0
for cropped_image in cropped_images :
    # crop된 이미지를 인코딩 및 변환
    cv2.imwrite(f"./build/{ii}.jpg",cropped_image)
    ii+=1
    _, encoded_image = cv2.imencode('.png', cropped_image)
    image_content = base64.b64encode(encoded_image.tobytes()).decode('utf-8')

    # Vision API에 이미지 전송하여 텍스트 추출
    image = vision.Image(content=image_content)
    response = client.document_text_detection(image=image)
    print(response.full_text_annotation.text)
    