import os
import fitz
from docx2pdf import convert

def image_converter(path):
    #word파일에서 바로 이미지로 변환하는 라이브러리가없어서 word파일이 들어오면 pdf파일로 변환해서 이미지로 변환시켰습니다.
    #찾아보니 word에서 바로 이미지로 변환해주는거 있긴한데 써보니까 이미지에 워터마크가 붙어버리네요..

    #파일명과 확장자 구분
    name, ext = os.path.splitext(path)

    # 파일명만 추출
    # name 변수는 파일 경로까지 담고 있기에
    filename = os.path.basename(path)
    filename = filename[:-4]

    if ext == ".docx":
        #word to pdf
        convert(path)
        path = f"{name}.pdf"

    elif ext != ".pdf":
        print("err")
        return 1
    
    #pdf to img
    doc = fitz.open(path)
    for i, page in enumerate(doc):
        img = page.get_pixmap(dpi=300)
        img.save(f"{name[:-len(filename)]}{filename}_{i}.png") #변환된 파일 저장경로
        print(f"{i}")

# PDF_FILE_PATH = "C:/Users/user/Downloads/test.pdf"
# image_converter(PDF_FILE_PATH)