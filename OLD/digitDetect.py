import cv2
import matplotlib.pyplot as plt
import numpy as np
from tensorflow.keras.models import load_model

def digit_detect(img):
    roi = cv2.resize(img, (28, 28),  cv2.INTER_AREA)

    roi = roi/255.0
    img_input = roi.reshape(1, 28, 28, 1)

    model = load_model('cnn-mnist-model.h5')
    prediction = model.predict(img_input)

    num = np.argmax(prediction)
    return num
