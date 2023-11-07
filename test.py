import cv2
import numpy as np
import os

answer_path = './시험지/SampleData/MCQ/T1/Answer'
answer_pages = []
X_SIZE = 2180
mark_template_path = './시험지/SampleData/mark_template'
for f in os.listdir(answer_path):
    if 'jpg' in f or 'png' in f or 'bmp' in f :
        img_array = np.fromfile(answer_path+'\\'+f, np.uint8)
        temp = cv2.imdecode(img_array,cv2.IMREAD_GRAYSCALE)
        
        #x=2180 으로 사이즈 조절
        temp = cv2.resize(temp, dsize=(X_SIZE, int(temp.shape[0] * (X_SIZE/temp.shape[1]))), interpolation=cv2.INTER_AREA)
        answer_pages.append(temp)

mark_templates = []
for f in os.listdir(mark_template_path):
    if 'jpg' in f or 'png' in f or 'bmp' in f :
        img_array = np.fromfile(mark_template_path+'\\'+f, np.uint8)
        temp = cv2.imdecode(img_array,cv2.IMREAD_GRAYSCALE)
        ret, temp = cv2.threshold(temp, 245, 255, cv2.THRESH_BINARY)
        #temp = cv2.resize(temp, dsize=(30,30), interpolation=cv2.INTER_AREA)
        mark_templates.append(temp)

test_page = answer_pages[1]
ret, thresh1 = cv2.threshold(test_page, 254, 255, cv2.THRESH_BINARY)
cv2.imshow("test",thresh1)
cv2.waitKey(0)