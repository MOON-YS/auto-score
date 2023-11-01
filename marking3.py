import os
import cv2
import numpy as np
from matplotlib import pyplot as plt
import random
import math



#두점 사이거리(정수반환)
def distance(pt1,pt2):
    res = math.sqrt(math.pow(pt1[0] - pt2[0],2)+math.pow(pt1[1] - pt2[1],2))
    return int(round(res))

def compare_image(image1, image2):
    orb = cv2.ORB_create()
    kp1, des1 = orb.detectAndCompute(image1,None)
    kp2, des2 = orb.detectAndCompute(image2,None)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    matches = bf.match(des1,des2)
    matches = sorted(matches, key = lambda x:x.distance)
    sim_ration = len(matches)/((len(kp1)+len(kp2))/2)
    return sim_ration

mark_template_path = 'E:\\Downlaods\\auto-score\\시험지\\SampleData\\mark_template'
mark_templates = []
for f in os.listdir(mark_template_path):
    if 'jpg' in f or 'png' in f or 'bmp' in f :
        img_array = np.fromfile(mark_template_path+'\\'+f, np.uint8)
        temp = cv2.imdecode(img_array,cv2.IMREAD_GRAYSCALE)
        mark_templates.append(temp)
        
#마킹 위치 좌표 반환 ex)[(204, 849), (210, 1684), (1157, 1725), (1552, 1237)]
def markingLoc(testImage,name=None):
    loc = [0,0]
    counter = 0
    for marker in mark_templates:
        #마킹 템플릿 이미지 크기만큼 w, h 지정
        w, h = marker.shape[::-1]
        #매치 템플릿
        result1 = cv2.matchTemplate(testImage, marker, cv2.TM_CCOEFF_NORMED)
        #임계값 설정
        loc_tmp = np.where(result1 >= 0.85)
        if counter == 0:
            loc[0] = np.concatenate((loc_tmp[0],loc_tmp[0]),0)
            loc[1] = np.concatenate((loc_tmp[1],loc_tmp[1]),0)
        else:
            loc[0] = np.concatenate((loc[0],loc_tmp[0]),0)
            loc[1] = np.concatenate((loc[1],loc_tmp[1]),0)
        counter += 1
        
    locs = []
    for pt in zip(*loc[::-1]):
        locs.append(pt)
    locs.sort(key=lambda x:(x[1], x[0]))
    k=0
    found_pt_n = []
    for pt in locs:
        if k == 0:
            found_pt_n.append(pt)
            prev1 = pt[0]
            prev2 = pt[1]
            k=1
            continue
        if (abs(prev1 - pt[0]) > 25) or (abs(prev2 - pt[1]) > 25):
            found_pt_n.append(pt)
            prev1 = pt[0]
            prev2 = pt[1]

    found_pt_n.sort(key=lambda x:(x[0], x[1]))
    print(found_pt_n)
    k=0
    found_ptn2 = []
    for pt in found_pt_n:
        if k == 0:
            found_ptn2.append(pt)
            prev1 = pt[0]
            prev2 = pt[1]
            k=1
            continue
        if (abs(prev1 - pt[0]) > 25) or (abs(prev2 - pt[1]) > 25):
            found_ptn2.append(pt)
            prev1 = pt[0]
            prev2 = pt[1]
    found_pt_n.sort(key=lambda x:(x[1], x[0]))
    k=0
    found_pt = []
    for pt in found_ptn2:
        if k == 0:
            found_pt.append(pt)
            prev1 = pt[0]
            prev2 = pt[1]
            k=1
            continue
        if (abs(prev1 - pt[0]) > 25) or (abs(prev2 - pt[1]) > 25):
            found_pt.append(pt)
            prev1 = pt[0]
            prev2 = pt[1]
    
    #매칭된 좌표값에 사각형 그리기 및 겹치는 좌표 제거하여 결과 저장
    for pt in found_pt:
        cv2.rectangle(testImage,pt, (pt[0]+w, pt[1]+h), (0, 0, 255), 2)

    #이미지 사이즈 조정후 출력
    ratio = 700.0 / testImage.shape[1]
    dim = (700, int(testImage.shape[0] * ratio))
    testImage = cv2.resize(testImage, dsize=dim, interpolation=cv2.INTER_AREA)
    #cv2.imshow(f"{name}.jpg",testImage)
    
    #좌표값 정렬 x오름 이후 y오름
    found_pt.sort(key=lambda x:(x[1], x[0]))
    
    return found_pt

#load test files
original_path = 'E:\\Downlaods\\auto-score\\시험지\\SampleData\\MCQ\\T1\\Original'
original_pages = []

for f in os.listdir(original_path):
    if 'jpg' in f or 'png' in f or 'bmp' in f :
        img_array = np.fromfile(original_path+'\\'+f, np.uint8)
        temp = cv2.imdecode(img_array,cv2.IMREAD_GRAYSCALE)
        original_pages.append(temp)

answer_path = 'E:\\Downlaods\\auto-score\\시험지\\SampleData\\MCQ\\T1\\Answer'
answer_pages = []

for f in os.listdir(answer_path):
    if 'jpg' in f or 'png' in f or 'bmp' in f :
        img_array = np.fromfile(answer_path+'\\'+f, np.uint8)
        temp = cv2.imdecode(img_array,cv2.IMREAD_GRAYSCALE)
        answer_pages.append(temp)

scanned_path = 'E:\\Downlaods\\auto-score\\시험지\\SampleData\\MCQ\\T1\\Scanned'
scanned_pages = []

for f in os.listdir(scanned_path):
    if 'jpg' in f or 'png' in f or 'bmp' in f :
        img_array = np.fromfile(scanned_path+'\\'+f, np.uint8)
        temp = cv2.imdecode(img_array,cv2.IMREAD_GRAYSCALE)
        scanned_pages.append(temp)
        
page_count = len(original_pages)
page_label = []

for i in range(0,len(scanned_pages)):
    for j in range(0,page_count):
        sim_ratio = compare_image(original_pages[j],scanned_pages[i])
        if sim_ratio >= 0.5:
            page_label.append(j)
            break

answer_loc = []
counter = 0
for image in answer_pages:
    answer_loc.append(markingLoc(image,str(counter)))
    counter+=1

qus_num = []
for num in answer_loc:
    qus_num.append(len(num))
    
#채점
scn_num = 0
for scn,page in zip(scanned_pages,page_label):
    scn_mark_loc = markingLoc(scn)
    scn_num+=1
    print(scn_mark_loc)
    #정답마킹 좌표와 답안마킹 좌표 거리계산, 15미만일시 정답 취급
    if len(answer_loc[page]) == len(scn_mark_loc):
        i=1
        for num in range(0,page):
            i += qus_num[num]
        print(f"File #{scn_num}={page+1}p")
        for a,b in zip(answer_loc[page],scn_mark_loc):
            if distance(a, b) < 15: print(f"{i}번: 정답")
            else : print(f"{i}번: 오답")
            i += 1
    else: print(f"ERR: File #{scn_num}={page+1}p 마킹갯수가 맞지 않습니다 {len(scn_mark_loc)} of {len(answer_loc[page])}")
    print("=======================")

cv2.waitKey(0)