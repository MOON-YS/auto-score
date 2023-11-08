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
original_path = './시험지/SampleData/MCQ/T4/Answer'
answer_path = './시험지/SampleData/MCQ/T4/Answer'
scanned_path = './시험지/SampleData/MCQ/T4/Scanned'

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
        

answer_loc = []
counter = 0
for image in answer_pages:
    answer_loc.append(markingLoc(image,str(counter)))
    counter+=1
    