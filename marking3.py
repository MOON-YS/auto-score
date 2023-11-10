import os
import cv2
import numpy as np
from matplotlib import pyplot as plt
import random
import math
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
def markingLoc(testImage,name=None):
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
    
    for pt in locs:
        cv2.rectangle(testImage,pt, (pt[0]+w, pt[1]+h), (255, 255, 255), 2)

    cv2.imwrite(f"./result/{name}.jpg",testImage)
    
    #좌표값 정렬 x오름 이후 y오름
    print(len(locs))
    return locs

#load test files
mark_template_path = './시험지/SampleData/mark_template'
original_path = './시험지/SampleData/MCQ/T2/Answer'
answer_path = './시험지/SampleData/MCQ/T2/Answer'
scanned_path = './시험지/SampleData/MCQ/T2/Scanned'

mark_templates = []
for f in os.listdir(mark_template_path):
    if 'jpg' in f or 'png' in f or 'bmp' in f :
        img_array = np.fromfile(mark_template_path+'\\'+f, np.uint8)
        temp = cv2.imdecode(img_array,cv2.IMREAD_GRAYSCALE)
        #ret, temp = cv2.threshold(temp, 245, 255, cv2.THRESH_BINARY)
        #temp = cv2.resize(temp, dsize=(30,30), interpolation=cv2.INTER_AREA)
        mark_templates.append(temp)
        
original_pages = []

for f in os.listdir(original_path):
    if 'jpg' in f or 'png' in f or 'bmp' in f :
        img_array = np.fromfile(original_path+'\\'+f, np.uint8)
        temp = cv2.imdecode(img_array,cv2.IMREAD_GRAYSCALE)
        #x=2180 으로 사이즈 조절
        temp = cv2.resize(temp, dsize=(X_SIZE, int(temp.shape[0] * (X_SIZE/temp.shape[1]))), interpolation=cv2.INTER_AREA)
        original_pages.append(temp)


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
        
page_count = len(original_pages)
page_label = []

for i in range(0,len(scanned_pages)):
    for j in range(0,page_count):
        sim_ratio = compare_image(original_pages[j],scanned_pages[i])
        print(sim_ratio)
        if sim_ratio >= 0.3:
            page_label.append(j)
            print(f"PROCESSING PAGE LABELING : {i+1} / {len(scanned_pages)} ({round(((i+1)/len(scanned_pages))*100)}%)",end="\r")
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
print("starting")
scn_num = 0
for scn,page in zip(scanned_pages,page_label):
    studentName = "Unknown"
    studentSerial = "Unknown"
    point = 0
    scn_num+=1
    scn_mark_loc = markingLoc(scn,f"__{scn_num}={page+1}")
    print(scn_mark_loc)
    #정답마킹 좌표와 답안마킹 좌표 거리계산, 15미만일시 정답 취급
    print(f"File #{scn_num} \nStudent Info : \n\tName : {studentName} \n\tSerial : {studentSerial} \n\tPage : {page+1}")
    if len(answer_loc[page]) == len(scn_mark_loc):
        i=1
        for num in range(0,page):
            i += qus_num[num]
        print(f"File #{scn_num}={page+1}p")
        for a,b in zip(answer_loc[page],scn_mark_loc):
            if distance(a, b) < 15: print(f"{i}번: 정답 [{point+5}]")
            else : print(f"{i}번: 오답 [{point}]")
            i += 1
    else: print(f"ERR: File #{scn_num}={page+1}p 마킹갯수가 맞지 않습니다 {len(scn_mark_loc)} of {len(answer_loc[page])}")
    print("=======================")

cv2.waitKey(0)