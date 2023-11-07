import cv2
import numpy as np
import matplotlib.pyplot as plt

X_SIZE = 700

img_array = np.fromfile("E:\\Downlaods\\auto-score\\시험지\\SampleData\\MCQ\\T1\\Original\\1.png", np.uint8)
original_page1 = cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)
original_page1 = cv2.resize(original_page1, dsize=(X_SIZE, int(original_page1.shape[0] * (X_SIZE/original_page1.shape[1]))), interpolation=cv2.INTER_AREA)
f = np.fft.fft2(original_page1)
fshift = np.fft.fftshift(f)
magnitude_spectrum = 20*np.log(np.abs(fshift))

img_array = np.fromfile("E:\\Downlaods\\auto-score\\시험지\\SampleData\\MCQ\\T1\\Scanned\\converted_30.png", np.uint8)
original_page2 = cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)
original_page2 = cv2.resize(original_page2, dsize=(X_SIZE, int(original_page1.shape[0] * (X_SIZE/original_page1.shape[1]))), interpolation=cv2.INTER_AREA)

# f = np.fft.fft2(original_page1)
# fshift = np.fft.fftshift(f)
# magnitude_spectrum = 20*np.log(np.abs(fshift))

# f = np.fft.fft2(original_page2)
# fshift = np.fft.fftshift(f)
# magnitude_spectrum2 = 20*np.log(np.abs(fshift))

# s1 = sum(sum(magnitude_spectrum))
# s2 = sum(sum(magnitude_spectrum2))
# print(str(s1) + " / " + str(s2))

# diffperpixel = sum(sum(magnitude_spectrum2 - magnitude_spectrum)) / (X_SIZE*int(original_page1.shape[0] * (X_SIZE/original_page1.shape[1])))
# print(diffperpixel)
kernel=np.ones((5,15),np.uint8)
ret, thresh1 = cv2.threshold(original_page1, 254, 255, cv2.THRESH_BINARY)
thresh1 = cv2.dilate(thresh1, kernel, iterations=1)

ret, thresh2 = cv2.threshold(original_page2, 200, 255, cv2.THRESH_BINARY_INV)
cv2.imwrite("ttt.jpg",thresh2)
cv2.imshow("test",thresh2)
cv2.waitKey(0)
