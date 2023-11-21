import os
import cv2
import numpy as np
from matplotlib import pyplot as plt
import math
import os
import cv2
import numpy as np
from google.cloud import vision
from google.oauth2 import service_account
import base64
import os
import fitz
from docx2pdf import convert
import torch
model = torch.hub.load('ultralytics/yolov5', 'custom', path='./best2.pt', force_reload=True)

def image_converter(path,fname):
    #word파일에서 바로 이미지로 변환하는 라이브러리가없어서 word파일이 들어오면 pdf파일로 변환해서 이미지로 변환시켰습니다.
    #찾아보니 word에서 바로 이미지로 변환해주는거 있긴한데 써보니까 이미지에 워터마크가 붙어버리네요..

    #파일명과 확장자 구분
    name, ext = os.path.splitext(path+"\\"+fname)
    if ext == ".docx":
        #word to pdf
        convert(path+"\\"+fname)
        path = f"{name}.pdf"

    elif ext != ".pdf":
        print("err")
        return 1
    
    #pdf to img
    doc = fitz.open(path+"\\"+fname)
    for i, page in enumerate(doc):
        img = page.get_pixmap(dpi=300)
        img.save(f"{path}/converted_{i}.png") #변환된 파일 저장경로
        print(f"{i}")

# 구글 키 파일 경로 설정
credentials_path = 'inbound-bee-234915-0490831a85a5.json'

# 구글 서비스 계정 인증 설정
credentials = service_account.Credentials.from_service_account_file(credentials_path)
client = vision.ImageAnnotatorClient(credentials=credentials)

X_SIZE = 2180
#두점 사이거리(정수반환)
def distance(pt1,pt2):
    res = math.sqrt(math.pow(pt1[0] - pt2[0],2)+math.pow(pt1[1] - pt2[1],2))
    return int(round(res))
#시험지 구분
def compare_image(image1, image2):
    downscaleTo = 200
    
    qimg = cv2.resize(image1, dsize=(downscaleTo, int(image1.shape[0] * (downscaleTo/image1.shape[1]))), interpolation=cv2.INTER_AREA)
    timg = cv2.resize(image2, dsize=(downscaleTo, int(image2.shape[0] * (downscaleTo/image2.shape[1]))), interpolation=cv2.INTER_AREA)

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
    
    sim_ration = len(good)/len(des1)
    return sim_ration

#마킹 위치 좌표 반환 ex)[(204, 849), (210, 1684), (1157, 1725), (1552, 1237)]
#마킹 위치 좌표 반환 ex)[(204, 849), (210, 1684), (1157, 1725), (1552, 1237)]
def markingLoc(testImage,name=None):
    #cv2.imwrite(f"./result/{name}_before.jpg",testImage)
    # 이미지를 YOLOv5 모델에 입력으로 전달하여 객체를 탐지
    results = model(testImage)

    # 좌표를 저장할 리스트
    detected_objects = []
    confidence_threshold = 0.65
    for detection in results.xyxy[0]:
    # 객체의 confidence가 threshold 이상인 경우에만 처리합니다.
        if detection[4].item() >= confidence_threshold:
            label = int(detection[5])
            bbox = detection[:4].int().cpu().numpy()
            x, y = bbox[0], bbox[1]
        
            # 좌표를 리스트에 저장
            detected_objects.append((x, y))

            #사각형으로 객체를 표시
            #cv2.rectangle(testImage, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)


    detected_objects.sort(key=lambda x:(x[1], x[0]))
    #중복 좌표 제거
    mask = np.zeros(testImage.shape[:2], np.uint8)
    w = 150
    h = 150
    locs = []
    for pt in detected_objects:
        if mask[pt[1] + int(round(h/2)), pt[0] + int(round(w/2))] != 255:
            mask[pt[1]:pt[1]+h, pt[0]:pt[0]+w] = 255
            locs.append(pt)
        
    #좌표를 출력
    #print(detected_objects)
    #cv2.imwrite(f"./result/ai_{name}.jpg",testImage)
    #좌표값 정렬 x오름 이후 y오름
    #print(len(detected_objects))
    return locs

def loadFiles(answer_path,scanned_path):
    """_summary_
    Args:
        answer_path (str): 정답 폴더 경로,
        scanned_path (str): 스캔된 시험지 폴더 경로
    """
    
    for f in os.listdir(answer_path):
        if 'pdf' in f or 'docx' in f:
            image_converter(answer_path,f)
    
    for f in os.listdir(scanned_path):
        if 'pdf' in f or 'docx' in f:
            image_converter(scanned_path,f)
    #load test files
    mark_template_path = './DataSet/mark_template'

    mark_templates = []
    for f in os.listdir(mark_template_path):
        if 'jpg' in f or 'png' in f or 'bmp' in f :
            img_array = np.fromfile(mark_template_path+'\\'+f, np.uint8)
            temp = cv2.imdecode(img_array,cv2.IMREAD_GRAYSCALE)
            #ret, temp = cv2.threshold(temp, 245, 255, cv2.THRESH_BINARY)
            #temp = cv2.resize(temp, dsize=(30,30), interpolation=cv2.INTER_AREA)
            mark_templates.append(temp)
        
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

    return scanned_pages,answer_pages,mark_templates

def get_id_name(scanned_png):
    #scanned_png = cv2.resize(scanned_png, dsize=(X_SIZE, int(scanned_png.shape[0] * (X_SIZE/scanned_png.shape[1]))), interpolation=cv2.INTER_AREA)
    #cv2.imshow(":",scanned_png)
    #cv2.setMouseCallback(':', onMouse)
    scanned_png = scanned_png[457:551,215:1952]
    _, encoded_image = cv2.imencode('.png', scanned_png)
    
    scanned_png = base64.b64encode(encoded_image.tobytes()).decode('utf-8')
    image = vision.Image(content=scanned_png)
    
    response = client.document_text_detection(image=image, image_context={"language_hints": ["ko"]})
    text = response.full_text_annotation.text
    print(text)
    x = text.replace(" ","")
    x = x.replace("이름:","")  
    x = x.replace("학번:","")
    arr = x.split("\n")
    arr = [v for v in arr if v]
    
    if len(arr) == 2:
        name = arr[0]
        serial = arr[1]
    else:
        name = "Unknown"
        serial = "Unknown"
    return name, serial

testpath = "./TestFile/Scanned/converted_1.png"
img_array = np.fromfile(testpath, np.uint8)
temp = cv2.imdecode(img_array,cv2.IMREAD_GRAYSCALE)
def onMouse(event, x, y, flags, param) :
    if event == cv2.EVENT_LBUTTONDOWN :
        print('왼쪽 마우스 클릭 했을 때 좌표 : ', x, y)
name, serial = get_id_name(temp)

def output(df) : 
    output_df = df.groupby(['Serial', 'Name'])['Point'].sum().to_frame().reset_index()
    output_df.columns = ['학번', '이름', '총점']
    print(output_df)
    return output_df, output_df['총점'].mean(),output_df['총점'].min(), output_df['총점'].max(), round(output_df['총점'].std(), 4)

cv2.waitKey(0)