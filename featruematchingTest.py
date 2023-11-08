import cv2
import numpy as np
X_SIZE = 200
 
img_array = np.fromfile('./시험지/SampleData/MCQ/T2/Answer/1.png', np.uint8)
qimg = cv2.imdecode(img_array,cv2.IMREAD_GRAYSCALE)
qimg = cv2.resize(qimg, dsize=(X_SIZE, int(qimg.shape[0] * (X_SIZE/qimg.shape[1]))), interpolation=cv2.INTER_AREA)

img_array = np.fromfile('./시험지/SampleData/MCQ/T2/Scanned/converted_64.png', np.uint8)
timg = cv2.imdecode(img_array,cv2.IMREAD_GRAYSCALE)
timg = cv2.resize(timg, dsize=(X_SIZE, int(timg.shape[0] * (X_SIZE/timg.shape[1]))), interpolation=cv2.INTER_AREA)

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

#res2 = cv2.drawMatchesKnn(qimg,kp1,timg,kp2,good,res2,flags=2)        

print(len(des1))
print(len(des2))
print(len(good))

# cv2.imshow("BF with SIFT",res2)
# cv2.waitKey(0)
# cv2.destroyAllWindows()