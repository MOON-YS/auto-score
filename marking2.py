import cv2
import numpy as np
import math

#시험지 샘플(1,2 = 칠; 3,4 = 체크)
testAnswer1= './시험지/SelectionSamples/answer1.jpg'
testAnswer2= './시험지/SelectionSamples/answer2.jpg'
testAnswer3= './시험지/SelectionSamples/answer3.jpg'
testAnswer4= './시험지/SelectionSamples/answer4.jpg'

#시험 답안지(체크)
testAnswerSheet= './시험지/SelectionSamples/test_answer_sheet.jpg'

#칠 마킹 템플릿
markingTemplateP1 = './시험지/SelectionSamples/markingTemplateP1.png'
markingTemplateP2 = './시험지/SelectionSamples/markingTemplateP2.png'
markingTemplateP3 = './시험지/SelectionSamples/markingTemplateP3.png'
markingTemplateP4 = './시험지/SelectionSamples/markingTemplateP4.png'

#체크 마킹 템플릿
markingTemplateC1 = './시험지/SelectionSamples/markingTemplateC1.png'
markingTemplateC2 = './시험지/SelectionSamples/markingTemplateC2.png'
markingTemplateC3 = './시험지/SelectionSamples/markingTemplateC3.png'
markingTemplateC4 = './시험지/SelectionSamples/markingTemplateC4.png'

#이미지 넘파이로 읽고 디코드
img_array = np.fromfile(testAnswerSheet, np.uint8)
testAnswerSheet = cv2.imdecode(img_array,cv2.IMREAD_GRAYSCALE)
img_array = np.fromfile(testAnswer1, np.uint8)
testAnswer1 = cv2.imdecode(img_array,cv2.IMREAD_GRAYSCALE)
img_array = np.fromfile(testAnswer2, np.uint8)
testAnswer2 = cv2.imdecode(img_array,cv2.IMREAD_GRAYSCALE)
img_array = np.fromfile(testAnswer3, np.uint8)
testAnswer3 = cv2.imdecode(img_array,cv2.IMREAD_GRAYSCALE)
img_array = np.fromfile(testAnswer4, np.uint8)
testAnswer4 = cv2.imdecode(img_array,cv2.IMREAD_GRAYSCALE)
img_array = np.fromfile(markingTemplateC1, np.uint8)
markingTemplateC1 = cv2.imdecode(img_array,cv2.IMREAD_GRAYSCALE)
img_array = np.fromfile(markingTemplateC2, np.uint8)
markingTemplateC2 = cv2.imdecode(img_array,cv2.IMREAD_GRAYSCALE)
img_array = np.fromfile(markingTemplateC3, np.uint8)
markingTemplateC3 = cv2.imdecode(img_array,cv2.IMREAD_GRAYSCALE)
img_array = np.fromfile(markingTemplateC4, np.uint8)
markingTemplateC4 = cv2.imdecode(img_array,cv2.IMREAD_GRAYSCALE)
img_array = np.fromfile(markingTemplateP1, np.uint8)
markingTemplateP1 = cv2.imdecode(img_array,cv2.IMREAD_GRAYSCALE)
img_array = np.fromfile(markingTemplateP2, np.uint8)
markingTemplateP2 = cv2.imdecode(img_array,cv2.IMREAD_GRAYSCALE)
img_array = np.fromfile(markingTemplateP3, np.uint8)
markingTemplateP3 = cv2.imdecode(img_array,cv2.IMREAD_GRAYSCALE)
img_array = np.fromfile(markingTemplateP4, np.uint8)
markingTemplateP4 = cv2.imdecode(img_array,cv2.IMREAD_GRAYSCALE)
#-> 실제작시 폴더째로 읽어와 반복문으로 작업

#두점 사이거리(정수반환)
def distance(pt1,pt2):
    res = math.sqrt(math.pow(pt1[0] - pt2[0],2)+math.pow(pt1[1] - pt2[1],2))
    return int(round(res))

#마킹 위치 좌표 반환 ex)[(204, 849), (210, 1684), (1157, 1725), (1552, 1237)]
def markingLoc(testImage,name=None):
    #마킹 템플릿 이미지 크기만큼 w, h 지정
    w, h = markingTemplateC1.shape[::-1]
    
    #매치 템플릿(칠마킹2회, 체크마킹2회)
    result1 = cv2.matchTemplate(testImage, markingTemplateP1, cv2.TM_CCOEFF_NORMED)
    result2 = cv2.matchTemplate(testImage, markingTemplateP2, cv2.TM_CCOEFF_NORMED)
    result3 = cv2.matchTemplate(testImage, markingTemplateP3, cv2.TM_CCOEFF_NORMED)
    result4 = cv2.matchTemplate(testImage, markingTemplateP4, cv2.TM_CCOEFF_NORMED)
    
    result5 = cv2.matchTemplate(testImage, markingTemplateC1, cv2.TM_CCOEFF_NORMED)
    result6 = cv2.matchTemplate(testImage, markingTemplateC2, cv2.TM_CCOEFF_NORMED)
    result7 = cv2.matchTemplate(testImage, markingTemplateC3, cv2.TM_CCOEFF_NORMED)
    result8 = cv2.matchTemplate(testImage, markingTemplateC4, cv2.TM_CCOEFF_NORMED)
    

    #임계값 설정
    loc1 = np.where(result1 >= 0.8)
    loc2 = np.where(result2 >= 0.8)
    loc3 = np.where(result3 >= 0.8)
    loc4 = np.where(result4 >= 0.8)
    loc5 = np.where(result5 >= 0.6)
    loc6 = np.where(result6 >= 0.6)
    loc7 = np.where(result7 >= 0.7)
    loc8 = np.where(result8 >= 0.7)
    
    #각 매칭된 결과들 병합
    loc = [0,0]
    loc[0] = np.concatenate((loc1[0],loc2[0]),0)
    loc[1] = np.concatenate((loc1[1],loc2[1]),0)
    loc[0] = np.concatenate((loc[0],loc3[0]),0)
    loc[1] = np.concatenate((loc[1],loc3[1]),0)
    loc[0] = np.concatenate((loc[0],loc4[0]),0)
    loc[1] = np.concatenate((loc[1],loc4[1]),0)
    loc[0] = np.concatenate((loc[0],loc5[0]),0)
    loc[1] = np.concatenate((loc[1],loc5[1]),0)
    loc[0] = np.concatenate((loc[0],loc6[0]),0)
    loc[1] = np.concatenate((loc[1],loc6[1]),0)
    loc[0] = np.concatenate((loc[0],loc7[0]),0)
    loc[1] = np.concatenate((loc[1],loc7[1]),0)
    loc[0] = np.concatenate((loc[0],loc8[0]),0)
    loc[1] = np.concatenate((loc[1],loc8[1]),0)
    
    locs = []
    for pt in zip(*loc[::-1]):
        locs.append(pt)
    locs.sort(key=lambda x:(x[1], x[0]))
    i=0
    found_pt = []
    for pt in locs:
        if i == 0:
            found_pt.append(pt)
            prev1 = pt[0]
            prev2 = pt[1]
            i=1
            continue
        if (abs(prev1 - pt[0]) > 20) or (abs(prev2 - pt[1]) > 20):
            found_pt.append(pt)
            prev1 = pt[0]
            prev2 = pt[1]
        prev1 = pt[0]
        prev2 = pt[1]
    i = 0
    #매칭된 좌표값에 사각형 그리기 및 겹치는 좌표 제거하여 결과 저장
    for pt in found_pt:
        cv2.rectangle(testImage,pt, (pt[0]+w, pt[1]+h), (0, 0, 255), 2)

    #이미지 사이즈 조정후 출력
    ratio = 700.0 / testImage.shape[1]
    dim = (700, int(testImage.shape[0] * ratio))
    testImage = cv2.resize(testImage, dsize=dim, interpolation=cv2.INTER_AREA)
    cv2.imshow(f"{name}.jpg",testImage)
    
    #좌표값 정렬 x오름 이후 y오름
    found_pt.sort(key=lambda x:(x[0], x[1]))
    
    return found_pt

answerLoc = markingLoc(testAnswerSheet,'Answer')
tests = []
studentNm = []
tests.append(markingLoc(testAnswer1,'s1 paint'))
studentNm.append('학생1 칠')
tests.append(markingLoc(testAnswer2,'s2 paint'))
studentNm.append('학생2 칠')
tests.append(markingLoc(testAnswer3,'s3 check'))
studentNm.append('학생3 체크')
tests.append(markingLoc(testAnswer4,'s4 check'))
studentNm.append('학생4 체크')

#1페이지 채점
for test,name in zip(tests,studentNm):
    #정답마킹 좌표와 답안마킹 좌표 거리계산, 15미만일시 정답 취급
    if len(answerLoc) == len(test):
        i = 1
        for a,b in zip(answerLoc,test):
            if distance(a, b) < 15:
                print(f"{name} p1 {i}번: 정답")
            else : print(f"{name} p1 {i}번: 오답")
            i += 1
    else: print(f"ERR: :{name}: 마킹갯수가 맞지 않습니다 {len(test)} of {len(answerLoc)}")
    print("=======================")

cv2.waitKey()
cv2.destroyAllWindows()