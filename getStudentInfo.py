import cv2
import numpy as np
import math
import os

scanned_png = './시험지/SampleData/MCQ/T1/Scanned/converted_35.png'
templateMatching_png = 'infoTemplate.png'

img_array = np.fromfile(scanned_png, np.uint8)
scanned_png = cv2.imdecode(img_array,cv2.IMREAD_GRAYSCALE)

img_array = np.fromfile(templateMatching_png, np.uint8)
templateMatching_png = cv2.imdecode(img_array,cv2.IMREAD_GRAYSCALE)

def find_multiple_occurrences(scanned_png, templateMatching_png, threshold=0.8):
    templateMatching_png = cv2.resize(templateMatching_png,(50,50), interpolation=cv2.INTER_AREA)
    # 템플릿 매칭을 수행합니다.
    result = cv2.matchTemplate(scanned_png, templateMatching_png, cv2.TM_CCOEFF_NORMED)
    
    # 매칭 결과에서 임계값 이상인 위치 찾기.
    locations = np.where(result >= threshold)

    occurrences = []
    mask = np.zeros(scanned_png.shape[:2], np.uint8)
    w = 50
    h = 50
    for pt in zip(*locations[::-1]):
        if mask[pt[1] + int(round(h/2)), pt[0] + int(round(w/2))] != 255:
            mask[pt[1]:pt[1]+h, pt[0]:pt[0]+w] = 255
            occurrences.append(pt)
    return occurrences

# 이미지 B의 여러 위치 찾기
occurrences = find_multiple_occurrences(scanned_png, templateMatching_png)
w, h = templateMatching_png.shape[::-1]

# 찾은 위치를 이미지 A에 표시
for pt in occurrences:
    cv2.rectangle(scanned_png, (pt[0]+60,pt[1]-20), (pt[0]+450,pt[1]+180), (0, 255, 0), 2)
    print(pt)

# 결과를 표시하거나 저장
ratio = 700.0 / scanned_png.shape[1]
dim = (700, int(scanned_png.shape[0] * ratio))
scanned_png = cv2.resize(scanned_png, dsize=dim, interpolation=cv2.INTER_AREA)
cv2.imshow('Result', scanned_png)

cv2.waitKey(0)
cv2.destroyAllWindows()