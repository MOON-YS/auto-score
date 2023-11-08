import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import random
X_SIZE = 2180

#load test files
mark_template_path = './시험지/SampleData/mark_template'
original_path = './시험지/SampleData/MCQ/T1/Answer'
answer_path = './시험지/SampleData/MCQ/T1/Answer'
scanned_path = './시험지/SampleData/MCQ/T1/Scanned'

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
croped = []
n = 0
for image in answer_pages:
    w, h = round(image.shape[0]/4) , round(image.shape[1]/2)
    tmp = []
    for i in range(0,image.shape[0]+1, round(image.shape[0]/4)):
        for j in range(0,image.shape[0]+1, round(image.shape[0]/2)):
            if (j+h < image.shape[0]) and (i+w < image.shape[1]) :
                tmp.append(image[j:j+h, i:i+w])
                cv2.imwrite(f"./croptest/{n}-{i}-{j}.jpg",image[j:j+h, i:i+w])
    croped.append(tmp)
    n+=1

def markingLoc(testImage,mark_templates, name=None):
    loc = [0,0]
    #ret, testImage = cv2.threshold(testImage, 245, 255, cv2.THRESH_BINARY)
    counter = 0
    for mark in mark_templates:
        #매치 템플릿
        result1 = cv2.matchTemplate(testImage, mark, cv2.TM_CCOEFF_NORMED)
        #임계값 설정
        loc_tmp = np.where(result1 >= 0.5)
        if counter == 0:
            loc[0] = np.concatenate((loc_tmp[0],loc_tmp[0]),0)
            loc[1] = np.concatenate((loc_tmp[1],loc_tmp[1]),0)
        else:
            loc[0] = np.concatenate((loc[0],loc_tmp[0]),0)
            loc[1] = np.concatenate((loc[1],loc_tmp[1]),0)
        counter += 1
    
    #중복 좌표 제거
    mask = np.zeros(testImage.shape[:2], np.uint8)
    w = mark_templates[0].shape[1]
    h = mark_templates[0].shape[0]
    locs = []
    
    for pt in zip(*loc[::-1]):
        if mask[pt[1] + int(round(h/2)), pt[0] + int(round(w/2))] != 255:
            mask[pt[1]:pt[1]+h, pt[0]:pt[0]+w] = 255
            locs.append(pt)

    #매칭된 좌표값에 사각형 그리기 및 겹치는 좌표 제거하여 결과 저장
    locs.sort(key=lambda x:(x[1], x[0]))
    
    #for pt in locs:
        #cv2.rectangle(testImage,pt, (pt[0]+w, pt[1]+h), (0, 0, 0), 2)

    #이미지 사이즈 조정후 출력
    #ratio = 1000.0 / testImage.shape[1]
    #dim = (1000, int(testImage.shape[0] * ratio))
    #testImage = cv2.resize(testImage, dsize=dim, interpolation=cv2.INTER_AREA)
    #cv2.imwrite(f"./result/{name}.jpg",testImage)
    
    return len(locs)

