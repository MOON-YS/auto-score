import cv2
import numpy as np
from ocr import detect_document  # Assuming you have an 'ocr' module
import copy

def getTextWithCropImg(path):
    isDragging = False  # Save mouse drag state
    x0, y0, w, h = -1, -1, -1, -1  # Save area selection coordinates
    blue, red = (255, 0, 0), (0, 0, 255)  # Color values
    scan_text_ex = ""

    def onMouse(event, x, y, flags, param):  # Mouse event handle function
        nonlocal isDragging, x0, y0, img, w, h, ori, ratio, scan_text_ex # Reference to nonlocal variables
        if event == cv2.EVENT_LBUTTONDOWN:  # Left mouse button down, start dragging
            isDragging = True
            x0 = x
            y0 = y
        elif event == cv2.EVENT_MOUSEMOVE:  # Mouse movement
            if isDragging:  # Dragging in progress
                img_draw = img.copy()  # Copy image to represent square picture
                cv2.rectangle(img_draw, (x0, y0), (x, y), blue, 2)  # Display the drag progress area
                cv2.imshow('img', img_draw)  # Print the square-shaped image on the screen
        elif event == cv2.EVENT_LBUTTONUP:  # Left mouse button up
            if isDragging:  # Stop dragging
                isDragging = False
                
                xo = x
                x0o = x0
                yo = y
                y0o= y0
                
                x = round(x/ratio)
                x0= round(x0/ratio)
                y = round(y/ratio)
                y0= round(y0/ratio)
                
                w = x - x0  # Calculate drag area width
                h = y - y0  # Calculate the height of the drag area
                print("x:%d, y:%d, w:%d, h:%d" % (x0, y0, w, h))
                if w > 0 and h > 0:  # If the width and height are positive, the drag direction is correct
                    img_draw = img.copy()  # Duplicate the image to display a square picture in the selection area
                    # Display a red rectangle in the selection area
                    cv2.rectangle(img_draw, (x0o, y0o), (xo, yo), red, 2)
                    cv2.imshow('img', img_draw)  # Display image with red square drawn on screen
                    roi = ori[y0:y0 + h, x0:x0 + w]  # Select only zero from the original image and specify it as ROI
                    #roi = cv2.resize(roi,dsize=(round(ratio*roi.shape[1]),round(ratio*roi.shape[0])),interpolation= cv2.INTER_LINEAR)
                    cv2.imshow('cropped', roi)  # Display ROI-specified area in a new window
                    cv2.moveWindow('cropped', 0, 0)  # Move the new window to the top left of the screen
                    cv2.imwrite('./cropped.jpg', roi)  # Save only the ROI area to a file
                    print("cropped.")
                    scan_text_ex = detect_document('./cropped.jpg')
                    #return scan_text_ex
                    
                else:
                    cv2.imshow('img', img)  # If the drag direction is wrong, output the original image without the square image.
                    print("Drag the area from the top left to the bottom right.")


    img_array = np.fromfile(path, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    ori = copy.deepcopy(img)
    
    ratio = 700.0 / img.shape[1]
    dim = (700, int(img.shape[0] * ratio))
    img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

    cv2.imshow('img', img)
    cv2.setMouseCallback('img', onMouse)
    cv2.waitKey()
    cv2.destroyAllWindows()
    return scan_text_ex

def getCropImg(path,fname):
    isDragging = False  # Save mouse drag state
    x0, y0, w, h = -1, -1, -1, -1  # Save area selection coordinates
    blue, red = (255, 0, 0), (0, 0, 255)  # Color values
    croped_file_path = None
    roi = None
    src_x0 = None
    src_y0 = None
    src_x1 = None
    src_y1 = None
    def onMouse(event, x, y, flags, param):  # Mouse event handle function
        # Reference to nonlocal variables
        nonlocal isDragging, x0, y0, img, w, h, ori, ratio, croped_file_path, roi,src_x0,src_y0,src_x1,src_y1 
        
        if event == cv2.EVENT_LBUTTONDOWN:  # Left mouse button down, start dragging
            isDragging = True
            x0 = x
            y0 = y
        elif event == cv2.EVENT_MOUSEMOVE:  # Mouse movement
            if isDragging:  # Dragging in progress
                img_draw = img.copy()  # Copy image to represent square picture
                cv2.rectangle(img_draw, (x0, y0), (x, y), blue, 2)  # Display the drag progress area
                cv2.imshow('img', img_draw)  # Print the square-shaped image on the screen
        elif event == cv2.EVENT_LBUTTONUP:  # Left mouse button up
            if isDragging:  # Stop dragging
                isDragging = False
                
                xo = x
                x0o = x0
                yo = y
                y0o= y0
                
                #make Original file Region
                x = round(x/ratio)
                x0= round(x0/ratio)
                y = round(y/ratio)
                y0= round(y0/ratio)
                
                src_x1 = x
                src_x0 = x0
                src_y1 = y
                src_y0 = y0
                
                w = x - x0  # Calculate drag area width
                h = y - y0  # Calculate the height of the drag area
                print("x:%d, y:%d, w:%d, h:%d" % (x0, y0, w, h))
                if w > 0 and h > 0:  # If the width and height are positive, the drag direction is correct
                    img_draw = img.copy()  # Duplicate the image to display a square picture in the selection area
                    # Display a red rectangle in the selection area
                    cv2.rectangle(img_draw, (x0o, y0o), (xo, yo), red, 2)
                    cv2.imshow('img', img_draw)  # Display image with red square drawn on screen
                    roi = ori[y0:y0 + h, x0:x0 + w]  # Select only zero from the original image and specify it as ROI
                    #roi = cv2.resize(roi,dsize=(round(ratio*roi.shape[1]),round(ratio*roi.shape[0])),interpolation= cv2.INTER_LINEAR)
                    cv2.imshow('cropped', roi)  # Display ROI-specified area in a new window
                    cv2.moveWindow('cropped', 0, 0)  # Move the new window to the top left of the screen
                    cv2.imwrite(f'./{fname}.jpg', roi)  # Save only the ROI area to a file
                    croped_file_path = f'./{fname}.jpg'
                    print("cropped.")
                    #scan_text_ex = detect_document('./cropped.jpg')
                    #return scan_text_ex
                    
                else:
                    cv2.imshow('img', img)  # If the drag direction is wrong, output the original image without the square image.
                    print("Drag the area from the top left to the bottom right.")


    img_array = np.fromfile(path, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    ori = copy.deepcopy(img)
    
    ratio = 700.0 / img.shape[1]
    dim = (700, int(img.shape[0] * ratio))
    img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

    cv2.imshow('img', img)
    cv2.setMouseCallback('img', onMouse)
    cv2.waitKey()
    cv2.destroyAllWindows()
    return src_x0,src_y0,src_x1,src_y1, croped_file_path