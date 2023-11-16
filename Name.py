from google.cloud import vision
from google.oauth2 import service_account
import cv2
import numpy as np
import base64

# 구글 키 파일 경로 설정
credentials_path = 'inbound-bee-234915-0490831a85a5.json'

# 구글 서비스 계정 인증 설정
credentials = service_account.Credentials.from_service_account_file(credentials_path)
client = vision.ImageAnnotatorClient(credentials=credentials)


def get_id_name(scanned_png, templateMatching_png):
    
    ret, ss = cv2.threshold(scanned_png, 127, 255, cv2.THRESH_BINARY_INV)
    ret, tt = cv2.threshold(templateMatching_png, 127, 255, cv2.THRESH_BINARY_INV)
    cv2.imshow("SS",ss)
    cv2.imshow("TT",tt)
    
    # templateMatching_png의 여러 위치 찾기
    # 템플릿 매칭을 수행합니다.
    result = cv2.matchTemplate(ss, tt, cv2.TM_CCOEFF_NORMED)
    # 매칭 결과에서 임계값 이상인 위치 찾기.
    locations = np.where(result >= 0.65)
    occurrences = []
    for loc in zip(*locations[::-1]):
        occurrences.append(loc)
    print(len(occurrences))
    
    # w, h = templateMatching_png.shape[::-1]
    # y1 = 0
    # Number_y2 = 0
    # x1 = 0
    # Number_x2 = 0
    
    # x1, y1 = pt
    # x2, y2 = (x1 + w, y1 + h)
    # Name_x1 = 0
    # Name_y1 = 0
    # Name_x2 = 0
    # Name_y2 = 0
    # Number_x1 = 0
    # Number_y1 = 0
    # Number_x2 = 0
    # Number_y2 = 0
    
    # # 이름/학번 영역
    # for pt in occurrences:
    #     x1, y1 = pt
    #     x2, y2 = (x1 + w, y1 + h)
    # # 이름 영역
    #     Name_x1 = x1 + 143
    #     Name_y1 = y1

    #     Name_x2 = x2 + 280
    #     Name_y2 = y2 
    # #학번 영역
    #     Number_x1 = x1 + 143
    #     Number_y1 = y1 + 70

    #     Number_x2 = x2 + 280
    #     Number_y2 = y2 + 70
    
    # Name_png = scanned_png[Name_y1:Name_y2, Name_x1:Name_x2]
    # ret, Name_png = cv2.threshold(Name_png, 127, 255, cv2.THRESH_BINARY_INV)
    # #cv2.imshow('Name_png', Name_png)

    # Number_png = scanned_png[Number_y1:Number_y2, Number_x1:Number_x2]
    # ret, Number_png = cv2.threshold(Number_png, 127, 255, cv2.THRESH_BINARY_INV)
    # #cv2.imshow('Number_png', Number_png)

    # test_png = scanned_png[y1:Number_y2, x1:Number_x2]
    # ret, test_png = cv2.threshold(test_png, 127, 255, cv2.THRESH_BINARY_INV)
    # #cv2.imshow('test_png', test_png)

    # # api로 보낼 이미지 리스트
    # cropped_images = []

    # cropped_images.append(Name_png)
    # cropped_images.append(Number_png)
    # # cropped_images.append(test_png)

    # name = ''
    # serial = ''
    # ii = 0
    # for cropped_image in cropped_images :
    #     # crop된 이미지를 인코딩 및 변환
    #     cv2.imwrite(f"./build/{ii}.jpg",cropped_image)
    #     ii = ii + 1
    #     _, encoded_image = cv2.imencode('.png', cropped_image)
    #     image_content = base64.b64encode(encoded_image.tobytes()).decode('utf-8')

    # # Vision API에 이미지 전송하여 텍스트 추출
    #     image = vision.Image(content=image_content)
    #     response = client.document_text_detection(image=image, image_context={"language_hints": ["ko"]})
    #     if ii == 1:
    #         name = response.full_text_annotation.text
    #     elif ii == 2:
    #         serial = response.full_text_annotation.text
        
        # for page in response.full_text_annotation.pages:
        #     for block in page.blocks:
        #         for paragraph in block.paragraphs:
        #             for word in paragraph.words:
        #                 word_text = ''.join([
        #                     symbol.text for symbol in word.symbols
        #                 ])
        #                 print('단어: {} (신뢰도: {})'.format(word_text, word.confidence))

        #                 for symbol in word.symbols:
        #                     if(symbol.confidence < 0.8):
        #                         print('\t{} (신뢰도: {})'.format(symbol.text, symbol.confidence))
        #return response.full_text_annotation.text

    #return name, serial


templateMatching_png = './DataSet/nameTemplate/star.jpg'
img_array = np.fromfile(templateMatching_png, np.uint8)
templateMatching_png = cv2.imdecode(img_array,cv2.IMREAD_GRAYSCALE)


scn = "./Err/10.jpg"
img_array = np.fromfile(scn, np.uint8)
scn = cv2.imdecode(img_array,cv2.IMREAD_GRAYSCALE)

get_id_name(scn,templateMatching_png)
cv2.waitKey(0)