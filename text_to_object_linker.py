from crop import *
from datastructure import *


scan_text = select_and_crop_image("./시험지/오지선다/수능 모의고사/01 성공적인 직업생활_문제지_page-0001.jpg")
Question1 = Question(q_text=scan_text)
print("fffff")
print(scan_text)
print(Question1.q_text)