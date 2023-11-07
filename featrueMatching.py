import os
import cv2
import numpy as np
import random
X_SIZE = 2180

mark_template_path = './시험지/SampleData/mark_template'
original_path = './시험지/SampleData/MCQ/T2/Answer'
answer_path = './시험지/SampleData/MCQ/T2/Answer'
scanned_path = './시험지/SampleData/MCQ/T2/Scanned'
#시험지 구분
def compare_image(image1, image2):
    orb = cv2.ORB_create()
    kp1, des1 = orb.detectAndCompute(image1,None)
    kp2, des2 = orb.detectAndCompute(image2,None)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    
    matches = bf.match(des1,des2)
    matches = sorted(matches, key = lambda x:x.distance)
    sim_ration = len(matches)/((len(kp1)+len(kp2))/2)
    
    res = cv2.drawMatches(image1, kp1, image2, kp2, matches, None, \
                     flags=cv2.DRAW_MATCHES_FLAGS_NOT_DRAW_SINGLE_POINTS)
    
    
    cv2.imshow('BFMatcher + ORB', res)
    cv2.imwrite('BFMatcher + ORB6.jpg', res)
    cv2.waitKey()
    cv2.destroyAllWindows()
    print(sim_ration)
    return sim_ration

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


compare_image(original_pages[1],scanned_pages[11])