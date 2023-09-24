import cv2
import numpy as np

isDragging = False
x0, y0, w, h = -1, -1, -1, -1
blue, red = (255, 0, 0), (0, 0, 255)

def onMouse(event, x, y, flags, param):
    global isDragging, x0, y0, src2,src,ratio
    if event == cv2.EVENT_LBUTTONDOWN:
        isDragging = True
        x0 = x
        y0 = y
    elif event == cv2.EVENT_MOUSEMOVE:
        if isDragging:
            img_draw = src2.copy()
            cv2.rectangle(img_draw, (x0, y0), (x, y), blue, 2)
            cv2.imshow('before', img_draw)
    elif event == cv2.EVENT_LBUTTONUP:
        if isDragging:
            isDragging = False
            xo = x
            x0o= x0
            yo = y
            y0o= y0
            
            x = round(x/ratio)
            x0= round(x0/ratio)
            y = round(y/ratio)
            y0= round(y0/ratio)
            w = x - x0
            h = y - y0
            if w > 0 and h > 0:
                img_draw = src2.copy()
                cv2.rectangle(img_draw, (x0o, y0o), (xo, yo), red, 2)
                cv2.imshow('before', img_draw)
                roi = src[y0:y0+h, x0:x0+w]
                #roi = cv2.resize(roi,dsize=(round(ratio*roi.shape[1]),round(ratio*roi.shape[0])),interpolation= cv2.INTER_LINEAR)
                cv2.imshow('cropped', roi)
                cv2.moveWindow('cropped', 0, 0)
                cv2.imwrite('./cropped.png', roi)
                cv2.imshow('cropped', roi)
                cv2.moveWindow('cropped', 0, 0)

            else:
                cv2.imshow('before', src2)
                print('drag should start from left-top side')

path = "./시험지/오지선다/수능 모의고사\[3학년] 23학년도 온라인모의 7차 예비평가-국어 (답 체크) (3).jpg"
img_array = np.fromfile(path,np.uint8)
src = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
#3783 2674
# > 높이를 1000으로 맞추려면 1000/shape[0]*shape[1]
ratio = 1500/src.shape[0]
src2 = cv2.resize(src,dsize=(round(ratio*src.shape[1]),1500),interpolation= cv2.INTER_LINEAR)


srcGray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
no, tresh = cv2.threshold(srcGray,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
cv2.imshow("before", tresh)
opening_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,1))
opening = cv2.morphologyEx(tresh, cv2.MORPH_OPEN, opening_kernel, iterations=1)
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20,20))
dilate = cv2.dilate(opening, kernel, iterations=2)

# Draw boxes
cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = cnts[0] if len(cnts) == 2 else cnts[1]
for c in cnts:
    area = cv2.contourArea(c)
    if area > 100:
        x,y,w,h = cv2.boundingRect(c)
        cv2.rectangle(src, (x, y), (x + w, y + h), (36,255,12), 3)
'''
bgrLower= np.array([0,0,0]) 
bgrUpper= np.array([255,255,165])
img_mask = cv2.inRange(src, bgrLower, bgrUpper) 
result = cv2.bitwise_and(src, src, mask=img_mask) 

cv2.imshow("before", src)
srcGray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
no, srcGray_n = cv2.threshold(srcGray,0,255,cv2.THRESH_OTSU)
= np.ones((2, 2), np.uint8)
erosion_image = cv2.dilate(srcGray_n, kernel, iterations=1)  #// make erosion image
erosion_image = 255-erosion_image

#erosion_image = cv2.resize(erosion_image,dsize=(0,0), fx=0.5,fy=0.5, interpolation= cv2.INTER_LINEAR)
src = cv2.resize(src,dsize=(0,0), fx=0.3,fy=0.3, interpolation= cv2.INTER_LINEAR) 
erosion_image = cv2.resize(erosion_image,dsize=(0,0), fx=0.3,fy=0.3, interpolation= cv2.INTER_LINEAR) 
'''


dilate = cv2.resize(dilate,dsize=(round(1500/src.shape[0]*src.shape[1]),1500),interpolation= cv2.INTER_LINEAR)
#cv2.imshow("before", dilate)
#cv2.imshow("at",src)
cv2.setMouseCallback('before', onMouse)
cv2.waitKey(0)
cv2.destroyAllWindows()
#kernel = np.ones((1, 1), np.uint8)
#erosion_image = cv2.erode(srcGray_n, kernel, iterations=1)  #// make erosion image
kernel 