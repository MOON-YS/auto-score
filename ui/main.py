import typing
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QWidget,QDialog
from PyQt5.QtCore import QSize,QCoreApplication
import cv2
import sys
import os
from pathlib import Path

from AutoScoreTools import loadFiles,markingLoc,distance,compare_image

Ui_Form = uic.loadUiType("./ui/intro.ui")[0]
answerDir = ""
scannedDir = ""
class AutoScoring(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("./ui/autoScore.ui",self)
        self.setFixedSize(QSize(535, 305))
        self.setWindowTitle("AutoScore")
        self.show()
    
    def runAutoScore(self):
        QCoreApplication.processEvents()
        scanned_pages,answer_pages,mark_templates = loadFiles(answerDir,scannedDir)
        page_count = len(answer_pages)
        page_label = []
        
        self.labelProgress.setText("페이지 분류 (1/3)")
        self.progressBar.setRange(0,len(scanned_pages))
        self.update()
        
        for i in range(0,len(scanned_pages)):
            for j in range(0,page_count):
                sim_ratio = compare_image(answer_pages[j],scanned_pages[i])
                if sim_ratio >= 0.3:
                    page_label.append(j)
                    self.txtBrowser.append(f"PROCESSING PAGE LABELING : {i+1} / {len(scanned_pages)} ({round(((i+1)/len(scanned_pages))*100)}%)")
                    self.progressBar.setValue(i+1)
                    self.update()
                    break
        
        self.labelProgress.setText("문제 갯수 확인중 (2/3)")
        self.progressBar.reset()
        self.progressBar.setRange(0,len(answer_pages))
        self.update()
        answer_loc = []
        counter = 0
        for image in answer_pages:
            answer_loc.append(markingLoc(image,mark_templates,str(counter)))
            self.txtBrowser.append(f"{counter+1} Page Has {len(answer_loc[counter])} Questions")
            counter+=1
            self.progressBar.setValue(counter)
            self.update()

        qus_num = []
        for num in answer_loc:
            qus_num.append(len(num))
        
        self.labelProgress.setText("채점중 (3/3)")
        self.progressBar.reset()
        self.progressBar.setRange(0,len(scanned_pages))
        Path('./ui/Err').mkdir(parents=True, exist_ok=True)
        scn_num = 0
        for scn,page in zip(scanned_pages,page_label):
            studentName = "Unknown"
            studentSerial = "Unknown"
            scn_num+=1
            scn_mark_loc = markingLoc(scn,mark_templates,f"__{scn_num}={page+1}")
            #정답마킹 좌표와 답안마킹 좌표 거리계산, 15미만일시 정답 취급
            if len(answer_loc[page]) == len(scn_mark_loc):
                i=1
                for num in range(0,page):
                    i += qus_num[num]
                self.txtBrowser.append(f"File #{scn_num} \nStudent Info : \n\tName : {studentName} \n\tSerial : {studentSerial} \n\tPage : {page+1}")
                for a,b in zip(answer_loc[page],scn_mark_loc):
                    if distance(a, b) < 15: self.txtBrowser.append(f"{i}번: 정답")
                    else : self.txtBrowser.append(f"{i}번: 오답")
                    i += 1
            else: 
                self.txtBrowser.append(f"ERR: File #{scn_num}={page+1}p 마킹갯수가 맞지 않습니다 {len(scn_mark_loc)} of {len(answer_loc[page])}")
                tmp = scn.copy()
                tmp = cv2.cvtColor(tmp,cv2.COLOR_GRAY2BGR)
                for pt in scn_mark_loc:
                    cv2.rectangle(tmp,pt, (pt[0]+50, pt[1]+50), (0, 0, 255), 2)
                cv2.imwrite(f"./Err/{scn_num}.jpg",tmp)

            self.txtBrowser.append("=======================")
            self.progressBar.setValue(scn_num)
        #scoring loop End
        self.txtBrowser.append("Scoring End")

class MyWindow(QtWidgets.QMainWindow, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(QSize(625, 470))
        self.initUi()
    
    def initUi(self):
        self.setWindowTitle("AutoScore")
        self.openAnswer.clicked.connect(self.openAns)
        self.openScanned.clicked.connect(self.openScn)
        self.introNextBtn.clicked.connect(self.introNext)
    
    def openAns(self):
        global answerDir
        answerDir = QtWidgets.QFileDialog.getExistingDirectory(self, 'Open Folder')
        self.folderDirAnswer.setText(answerDir)
        fileList = os.listdir(answerDir)
        fileCount = len(fileList)
        self.countAnswerPage.setText(str(fileCount) + "개의 파일을 찾았습니다.")
        
    def openScn(self):
        global scannedDir
        scannedDir = QtWidgets.QFileDialog.getExistingDirectory(self, 'Open Folder')
        self.folderDirScanned.setText(scannedDir)
        fileList = os.listdir(scannedDir)
        fileCount = len(fileList)
        self.countScannedPage.setText(str(fileCount) + "개의 파일을 찾았습니다.")
    
    def introNext(self):
        global scannedDir, answerDir
        if len(os.listdir(scannedDir)) < len(os.listdir(answerDir)):
            self.introErrMsg.setStyleSheet("Color : red")
            self.introErrMsg.setText("채점할 시험지 갯수가 적습니다. 파일경로를 확인해주세요")
        elif scannedDir == "" or answerDir == "":
            self.introErrMsg.setStyleSheet("Color : red")
            self.introErrMsg.setText("폴더 경로를 입력해주세요")
        elif scannedDir == answerDir:
            self.introErrMsg.setStyleSheet("Color : red")
            self.introErrMsg.setText("두 폴더 경로가 같습니다.")
        else:
            self.introErrMsg.setStyleSheet("Color : green")
            self.introErrMsg.setText("정상")
            Window2 = AutoScoring()
            self.hide()
            Window2.runAutoScore()
            
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MyWindow = MyWindow()
    MyWindow.show()
    app.exec_()