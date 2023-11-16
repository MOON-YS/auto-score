import os
import cv2
import numpy as np
from matplotlib import pyplot as plt
import math
import os
import cv2
import numpy as np
from matplotlib import pyplot as plt
from google.cloud import vision
from google.oauth2 import service_account
import io
import base64

# 구글 키 파일 경로 설정
credentials_path = 'inbound-bee-234915-0490831a85a5.json'

# 구글 서비스 계정 인증 설정
credentials = service_account.Credentials.from_service_account_file(credentials_path)
client = vision.ImageAnnotatorClient(credentials=credentials)

X_SIZE = 2180
#두점 사이거리(정수반환)
def distance(pt1,pt2):
    res = math.sqrt(math.pow(pt1[0] - pt2[0],2)+math.pow(pt1[1] - pt2[1],2))
    return int(round(res))
#시험지 구분
def compare_image(image1, image2):
    downscaleTo = 200
    
    qimg = cv2.resize(image1, dsize=(downscaleTo, int(image1.shape[0] * (downscaleTo/image1.shape[1]))), interpolation=cv2.INTER_AREA)
    timg = cv2.resize(image2, dsize=(downscaleTo, int(image2.shape[0] * (downscaleTo/image2.shape[1]))), interpolation=cv2.INTER_AREA)

    res2 = None

    sift = cv2.xfeatures2d.SIFT_create()

    kp1, des1 = sift.detectAndCompute(qimg,None)
    kp2, des2 = sift.detectAndCompute(timg,None)

    # 초깃값으로 파라미터 지정
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1,des2,k=2)

    # ratio test 적용
    good = []

    for m,n in matches:
        if m.distance < 0.75*n.distance:
            good.append([m])
    
    sim_ration = len(good)/len(des1)
    return sim_ration

#마킹 위치 좌표 반환 ex)[(204, 849), (210, 1684), (1157, 1725), (1552, 1237)]
def markingLoc(testImage,mark_templates,name=None):
    loc = [0,0]
    testImage = cv2.blur(testImage,(3,2))
    ret, testImage = cv2.threshold(testImage, 250, 255, cv2.THRESH_BINARY_INV)
    counter = 0
    for mark in mark_templates:
        #매치 템플릿
        result1 = cv2.matchTemplate(testImage, mark, cv2.TM_CCOEFF_NORMED)
        #임계값 설정
        loc_tmp = np.where(result1 >= 0.9)
        if counter == 0:
            loc[0] = np.concatenate((loc_tmp[0],loc_tmp[0]),0)
            loc[1] = np.concatenate((loc_tmp[1],loc_tmp[1]),0)
        else:
            loc[0] = np.concatenate((loc[0],loc_tmp[0]),0)
            loc[1] = np.concatenate((loc[1],loc_tmp[1]),0)
        counter += 1
    
    #중복 좌표 제거
    mask = np.zeros(testImage.shape[:2], np.uint8)
    w = 50
    h = 50
    locs = []
    
    for pt in zip(*loc[::-1]):
        if mask[pt[1] + int(round(h/2)), pt[0] + int(round(w/2))] != 255:
            mask[pt[1]:pt[1]+h, pt[0]:pt[0]+w] = 255
            locs.append(pt)

    #매칭된 좌표값에 사각형 그리기 및 겹치는 좌표 제거하여 결과 저장
    locs.sort(key=lambda x:(x[1], x[0]))
    
    #좌표값 정렬 x오름 이후 y오름
    return locs

def loadFiles(answer_path,scanned_path):
    """_summary_
    Args:
        answer_path (str): 정답 폴더 경로,
        scanned_path (str): 스캔된 시험지 폴더 경로
    """
    #load test files
    mark_template_path = './DataSet/mark_template'

    mark_templates = []
    for f in os.listdir(mark_template_path):
        if 'jpg' in f or 'png' in f or 'bmp' in f :
            img_array = np.fromfile(mark_template_path+'\\'+f, np.uint8)
            temp = cv2.imdecode(img_array,cv2.IMREAD_GRAYSCALE)
            #ret, temp = cv2.threshold(temp, 245, 255, cv2.THRESH_BINARY)
            #temp = cv2.resize(temp, dsize=(30,30), interpolation=cv2.INTER_AREA)
            mark_templates.append(temp)
        
    answer_pages = []
    for f in os.listdir(answer_path):
        if 'jpg' in f or 'png' in f or 'bmp' in f :
            img_array = np.fromfile(answer_path+'\\'+f, np.uint8)
            temp = cv2.imdecode(img_array,cv2.IMREAD_GRAYSCALE)
            #x=2180 으로 사이즈 조절
            temp = cv2.resize(temp, dsize=(X_SIZE, int(temp.shape[0] * (X_SIZE/temp.shape[1]))), interpolation=cv2.INTER_AREA)
            answer_pages.append(temp)


    scanned_pages = []
    for f in os.listdir(scanned_path):
        if 'jpg' in f or 'png' in f or 'bmp' in f :
            img_array = np.fromfile(scanned_path+'\\'+f, np.uint8)
            temp = cv2.imdecode(img_array,cv2.IMREAD_GRAYSCALE)
            #x=2180 으로 사이즈 조절
            temp = cv2.resize(temp, dsize=(X_SIZE, int(temp.shape[0] * (X_SIZE/temp.shape[1]))), interpolation=cv2.INTER_AREA)
            scanned_pages.append(temp)

    return scanned_pages,answer_pages,mark_templates

def get_id_name(scanned_png, templateMatching_png):
    # templateMatching_png의 여러 위치 찾기
    # 템플릿 매칭을 수행합니다.
    result = cv2.matchTemplate(scanned_png, templateMatching_png, cv2.TM_CCOEFF_NORMED)
    # 매칭 결과에서 임계값 이상인 위치 찾기.
    locations = np.where(result >= 0.8)
    occurrences = []
    for loc in zip(*locations[::-1]):
        occurrences.append(loc)
        
    w, h = templateMatching_png.shape[::-1]
    y1 = 0
    Number_y2 = 0
    x1 = 0
    Number_x2 = 0
    # 이름/학번 영역
    for pt in occurrences:
        x1, y1 = pt
        x2, y2 = (x1 + w, y1 + h)
    # 이름 영역
        Name_x1 = x1 + 143
        Name_y1 = y1

        Name_x2 = x2 + 280
        Name_y2 = y2 
    #학번 영역
        Number_x1 = x1 + 143
        Number_y1 = y1 + 70

        Number_x2 = x2 + 280
        Number_y2 = y2 + 70
    
    Name_png = scanned_png[Name_y1:Name_y2, Name_x1:Name_x2]
    ret, Name_png = cv2.threshold(Name_png, 127, 255, cv2.THRESH_BINARY_INV)
    #cv2.imshow('Name_png', Name_png)

    Number_png = scanned_png[Number_y1:Number_y2, Number_x1:Number_x2]
    ret, Number_png = cv2.threshold(Number_png, 127, 255, cv2.THRESH_BINARY_INV)
    #cv2.imshow('Number_png', Number_png)

    test_png = scanned_png[y1:Number_y2, x1:Number_x2]
    ret, test_png = cv2.threshold(test_png, 127, 255, cv2.THRESH_BINARY_INV)
    #cv2.imshow('test_png', test_png)

    # api로 보낼 이미지 리스트
    cropped_images = []

    cropped_images.append(Name_png)
    cropped_images.append(Number_png)
    # cropped_images.append(test_png)

    name = ''
    serial = ''
    ii = 0
    for cropped_image in cropped_images :
        # crop된 이미지를 인코딩 및 변환
        cv2.imwrite(f"./build/{ii}.jpg",cropped_image)
        ii = ii + 1
        _, encoded_image = cv2.imencode('.png', cropped_image)
        image_content = base64.b64encode(encoded_image.tobytes()).decode('utf-8')

    # Vision API에 이미지 전송하여 텍스트 추출
        image = vision.Image(content=image_content)
        response = client.document_text_detection(image=image, image_context={"language_hints": ["ko"]})
        if ii == 1:
            name = response.full_text_annotation.text
        elif ii == 2:
            serial = response.full_text_annotation.text
        
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

    return name, serial