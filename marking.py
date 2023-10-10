import cv2
import json
import numpy as np
import datastructure
from ocr import detect_number_from_img
from digitDetect import digit_detect
#get question info

with open('./test.json', 'r',encoding='utf-8') as f:
    qData = json.load(f)
    qData = json.loads(qData)
    
qFile = "./시험지/오지선다/수능 모의고사/01 성공적인 직업생활_문제지_page-0001.jpg"

#testFile = "./시험지/오지선다/수능 모의고사/01 성공적인 직업생활_문제지_page-0001 답안체크 정답.jpg"
#testFile = './시험지/오지선다/수능 모의고사/01 성공적인 직업생활_문제지_page-0001 답안체크 오답.jpg'
#testFile = './시험지/오지선다/수능 모의고사/01 성공적인 직업생활_문제지_page-0001 답안번호 정답.jpg'
testFile = './시험지/오지선다/수능 모의고사/01 성공적인 직업생활_문제지_page-0001 답안번호 오답.jpg'

img_array = np.fromfile(testFile, np.uint8)
ans_img = cv2.imdecode(img_array,cv2.IMREAD_COLOR)
img_array = np.fromfile(qFile, np.uint8)
q_img = cv2.imdecode(img_array,cv2.IMREAD_COLOR)

correct_ans = int(qData["q_answer"])

sel_x0 = qData["q_selections"]["x0"]
sel_y0 = qData["q_selections"]["y0"]
sel_x1 = qData["q_selections"]["x1"]
sel_y1 = qData["q_selections"]["y1"]

## select box checked
sel_w = sel_x1 - sel_x0
sel_h = sel_y1 - sel_y0

s_roi1 = q_img[sel_y0:sel_y0 + sel_h, sel_x0:sel_x0 + sel_w].copy() 
s_roi2 = ans_img[sel_y0:sel_y0 + sel_h, sel_x0:sel_x0 + sel_w].copy()  

roi1 = cv2.cvtColor(s_roi1, cv2.COLOR_BGR2GRAY)
roi2 = cv2.cvtColor(s_roi2, cv2.COLOR_BGR2GRAY)
#cv2.imshow("Original - Gray", roi1)
#cv2.imshow("Checked - Gray", roi2)
_,roi1_thresh_inv = cv2.threshold(roi1,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
_,roi1_thresh = cv2.threshold(roi1,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
#cv2.imshow("Original - Threshold (BINARY_INV + OTSU)", roi1_thresh_inv)
#cv2.imshow("Original - Threshold (BINARY + OTSU)", roi1_thresh)

_,roi2 = cv2.threshold(roi2,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
#cv2.imshow("Checked - Threshold(BINARY_INV + OTSU)", roi2)
r1_r2 = cv2.bitwise_and(roi2,roi1_thresh)
#cv2.imshow("and(Checked,Original)", r1_r2)
erode = cv2.erode(r1_r2, np.ones((2,1)), iterations=2)
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
r1_r2 = cv2.dilate(erode, kernel, iterations=2)
#cv2.imshow("Checked - Erode&Dilate", r1_r2)
checked = None
checkedMidPt = None
#find check box
cnts = cv2.findContours(r1_r2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = cnts[0] if len(cnts) == 2 else cnts[1]
i = 0
for c in cnts:
    area = cv2.contourArea(c)
    if area > 10:
        x,y,w,h = cv2.boundingRect(c)
        cv2.rectangle(s_roi2, (x, y), (x + w, y + h), (0,0,0), 2)
        checked = [x, y,x + w, y + h]
        checkedMidPt = (round((2*x+w)/2),y+h)
        cv2.circle(s_roi2,checkedMidPt,10,(0,0,0),-1)
#cv2.imshow("Checked - Find Contours", s_roi2)
if checked != None:
    sel = []

    opening_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,1))
    opening = cv2.morphologyEx(roi1_thresh_inv, cv2.MORPH_OPEN, opening_kernel, iterations=1)#노이즈제거
    #cv2.imshow("Original - MorphologyEx", opening)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10,3))
    dilate = cv2.dilate(opening, kernel, iterations=2)
    #cv2.imshow("Original - Dilate", dilate)

    #find selection box
    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    i = 0
    for c in cnts:
        area = cv2.contourArea(c)
        if area > 1000:
            x,y,w,h = cv2.boundingRect(c)
            cv2.rectangle(s_roi1, (x, y), (x + w, y + h), (0,0,0), 1)
            sel.append([x,y,x + w, y + h])
    sel.sort(key=lambda x:(x[1], x[0]))
    #cv2.imshow("Original - Found select", s_roi1)
    
    i = 0
    for box in sel :
        i = i+1
        bin1 = np.zeros((roi1.shape[0],roi1.shape[1],3), np.uint8)
        bin2 = np.zeros((roi1.shape[0],roi1.shape[1],3), np.uint8)
        bin1 = cv2.rectangle(bin1,(box[0],box[1]),(box[2],box[3]),(255,255,255),-1)
        bin2 = cv2.circle(bin2,checkedMidPt,10,(255,255,255),-1)
        #cv2.imshow(f'box - {i}', bin1)
        result = cv2.bitwise_and(bin1,bin2)
        #cv2.imshow(f'box{i}&&check box', result)
        sum_of_and = sum(sum(sum(result)))
        if sum_of_and != 0:
            if i == correct_ans:
                print(f"Student Choose Correct Answer : {i}")
            else: print(f"Student Choose Wrong Answer : {i}")
        
else:
    print("Check not found")
    
    x0 = qData["src_crd"]["x0"]
    y0 = qData["src_crd"]["y0"]
    x1 = qData["src_crd"]["x1"]
    y1 = qData["src_crd"]["y1"]
    
    w = x1 - x0
    h = y1 - y0
    
    a_roi = q_img[y0:y0 + h, x0:x0 + w].copy() 
    q_roi = ans_img[y0:y0 + h, x0:x0 + w].copy()  
    
    #cv2.imshow("Answer All", a_roi)
    #cv2.imshow("Question ALL", q_roi)
    
    a_roi = cv2.cvtColor(a_roi, cv2.COLOR_BGR2GRAY)
    q_roi = cv2.cvtColor(q_roi, cv2.COLOR_BGR2GRAY)
    _,a_roi_thresh_inv = cv2.threshold(a_roi,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    _,a_roi_thresh = cv2.threshold(a_roi,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    #cv2.imshow("Answer - Thresh Inv", a_roi_thresh_inv)
    #cv2.imshow("Question - Thresh", a_roi_thresh)
    _,q_roi_thresh = cv2.threshold(q_roi,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    #cv2.imshow("Answer Threshold", q_roi_thresh)
    r1_r2 = cv2.bitwise_and(a_roi_thresh,q_roi_thresh)
    #cv2.imshow("Answer Threshold & Question Thresh", r1_r2)
    opening_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
    opening = cv2.morphologyEx(r1_r2, cv2.MORPH_OPEN, opening_kernel, iterations=1)#노이즈제거
    number = None
    cnts = cv2.findContours(opening, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        area = cv2.contourArea(c)
        if area > 10:
            x,y,w,h = cv2.boundingRect(c)
            #cv2.rectangle(opening, (x, y), (x + w, y + h), (255,255,255), 2)
            number = [x, y,x + w, y + h]

    number_img = opening[y-10:y + h+10, x-10:x + w+10].copy()
    number_img = cv2.erode(number_img, np.ones((2,1)), iterations=2)
    #cv2.imshow("bit wise and", number_img)
    ans_num = digit_detect(number_img)
    #print(ans_num)
    if ans_num == correct_ans: print(f"Student Choose Correct Answer : {ans_num}")
    else: print(f"Student Choose Wrong Answer : {ans_num}")


cv2.waitKey()
cv2.destroyAllWindows()