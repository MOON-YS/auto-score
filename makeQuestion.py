from crop import *
from datastructure import *
import json

print("=======On Linker========")
#print(scan_text)

id = input("문제 번호 : ")
type = input("문제 유형 : ")
answer = input("문제 정답 : ")
points = input("점수 : ")
print("문제영역 드래그")
x0,y0,x1,y1,fpath = getCropImg("./시험지/오지선다/수능 모의고사/01 성공적인 직업생활_문제지_page-0001.jpg","q1_all")
src_crd = {"x0" : x0,"y0" : y0,"x1" : x1,"y1" : y1}
#print("문항내용 드래그")
#content = getTextWithCropImg("./시험지/오지선다/수능 모의고사/01 성공적인 직업생활_문제지_page-0001.jpg")
#print("지문 드래그")
#x0,y0,x1,y1,text = getCropImg("./시험지/오지선다/수능 모의고사/01 성공적인 직업생활_문제지_page-0001.jpg","q1_text")
print("선택지 드래그")
x0,y0,x1,y1,_ = getCropImg("./시험지/오지선다/수능 모의고사/01 성공적인 직업생활_문제지_page-0001.jpg","q1_sel")
sel_crd = {"x0" : x0,"y0" : y0,"x1" : x1,"y1" : y1}
#print("보기 드래그")
#example = getTextWithCropImg("./시험지/오지선다/수능 모의고사/01 성공적인 직업생활_문제지_page-0001.jpg")
Question1 = Question(src_crd,id,type,None,answer,None,None,sel_crd,None,points)
#print(Question1.q_text)
print(Question1.json)

with open("./test.json", 'w', encoding='utf-8') as file:
    json.dump(Question1.json, file, indent="\t", ensure_ascii=False)
    