import shutil
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QWidget,QDialog, QTableWidget , QTableWidgetItem,  QFileDialog
from PyQt5.QtCore import QSize,QCoreApplication,QEventLoop, Qt
import cv2
import sys
import os
from pathlib import Path
import pandas as pd
from AutoScoreTools import loadFiles,markingLoc,distance,compare_image,get_id_name,output
from questionCheck import QcWindow
from errCheck import EcWindow
import numpy as np

Ui_Form = uic.loadUiType("intro.ui")[0]
answerDir = ""
scannedDir = ""
templatePngPath = "./DataSet/nameTemplate/star.jpg"
img_array = np.fromfile(templatePngPath, np.uint8)
templatePng = cv2.imdecode(img_array,cv2.IMREAD_GRAYSCALE)

class AutoScoring(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("autoScore.ui",self)
        self.setFixedSize(QSize(535, 325))
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
        qCounter = 1
        answerData = pd.DataFrame(columns=['페이지','번호','정답좌표'])
        if os.path.exists('./AnswerPage') == True : shutil.rmtree('./AnswerPage')
        Path('AnswerPage').mkdir(parents=True, exist_ok=True)
        for image in answer_pages:
            answer_loc.append(markingLoc(image,str(counter)))
            self.txtBrowser.append(f"{counter+1} Page Has {len(answer_loc[counter])} Questions")
            tmp = image.copy()
            tmp = cv2.cvtColor(tmp,cv2.COLOR_GRAY2BGR)
            for loc in answer_loc[counter]:
                cv2.rectangle(tmp, loc, (loc[0]+50, loc[1]+50), (0, 0, 255), 2)
                answerData.loc[len(answerData.index)] = [counter+1,qCounter,str(loc).replace("(","").replace(")","")]
                qCounter += 1
            cv2.imwrite(f"./AnswerPage/{counter}.jpg",tmp)
            counter+=1
            self.progressBar.setValue(counter)
            self.update()
        qus_num = []

        #배점 입력 받기 및 문제 갯수 검증
        window = QcWindow()
        window.setAttribute(Qt.WA_DeleteOnClose)
        window.setQData(answerData)
        window.setImgPath("./AnswerPage")
        window.show()
        loop = QEventLoop()
        window.destroyed.connect(loop.quit)
        loop.exec()
        answerData = window.answerData
        score_arr = answerData["배점"].to_list()
        

        for num in answer_loc:
            qus_num.append(len(num))
        
        self.labelProgress.setText("채점중 (3/3)")
        self.progressBar.reset()
        self.progressBar.setRange(0,len(scanned_pages))
        if os.path.exists('./Err') == True : shutil.rmtree('./Err')
        Path('Err').mkdir(parents=True, exist_ok=True)
        scn_num = 0
        err_cnt = 0
        errData = pd.DataFrame(columns=['파일번호','페이지','문제번호','답안좌표'])
        errFnM = pd.DataFrame(columns=['파일번호','이름','학번'])
        columns = ['Name', 'Serial', 'Page', 'Question_Num', 'isCorrect', 'Point', 'Err']
        df = pd.DataFrame([], columns=columns)
        for scn,page in zip(scanned_pages,page_label):
            studentName, studentSerial = get_id_name(scn)
            scn_num+=1
            scn_mark_loc = markingLoc(scn,f"__{scn_num}={page+1}")
            #정답마킹 좌표와 답안마킹 좌표 거리계산, 15미만일시 정답 취급
            i=1 # i : 문제 번호
            for num in range(0,page):
                i += qus_num[num]
            if len(answer_loc[page]) == len(scn_mark_loc):
                isCorrect = False
                point = 0
                self.txtBrowser.append(f"File #{scn_num} \nStudent Info : \n\tName : {studentName} \n\tSerial : {studentSerial} \n\tPage : {page+1}")
                for a,b in zip(answer_loc[page],scn_mark_loc):
                    if distance(a, b) < 15: 
                        self.txtBrowser.append(f"{i}번: 정답 {score_arr[i-1]}점")
                        isCorrect = True
                        point = int(score_arr[i-1])
                    else : self.txtBrowser.append(f"{i}번: 오답")
                    i += 1
                    errMsg = ""
                    if studentName == "Unknown" or studentSerial == "Unknown":
                        errMsg = f"이름 및 학번 인식에 실패했습니다. File #{scn_num}"
                    data = pd.Series([studentName, studentSerial, page+1, i, isCorrect, point, errMsg], index=columns)
                    df = df._append(data, ignore_index=True)
                
                
            else: 
                self.txtBrowser.append(f"ERR: File #{scn_num}={page+1}p 마킹갯수가 맞지 않습니다 {len(scn_mark_loc)} of {len(answer_loc[page])}")
                err_cnt +=1
                tmp = scn.copy()
                tmp = cv2.cvtColor(tmp,cv2.COLOR_GRAY2BGR)
                errFnM.loc[len(errData.index)] = [str(scn_num),studentName,studentSerial]
                for pt in scn_mark_loc:
                    cv2.rectangle(tmp,pt, (pt[0]+50, pt[1]+50), (0, 0, 255), 2)
                    cv2.putText(tmp,f"{pt}",pt, cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 1, cv2.LINE_AA)
                    errData.loc[len(errData.index)] = [scn_num,page+1,i,str(pt).replace("(","").replace(")","")]
                    i+=1
                    
                cv2.imwrite(f"./Err/{scn_num}.jpg",tmp)

            self.txtBrowser.append("=======================")
            self.progressBar.setValue(scn_num)
        #scoring loop End
        self.txtBrowser.append("First Scoring End")
        

        #배점 입력 받기 및 문제 갯수 검증
        window = EcWindow()
        window.setAttribute(Qt.WA_DeleteOnClose)
        window.setQData(errData)
        window.setImgPath("./Err")
        window.show()
        loop = QEventLoop()
        window.destroyed.connect(loop.quit)
        loop.exec()
        errChecked = window.answerData
        
        #재채점
        self.labelProgress.setText("재 채점중")
        self.progressBar.reset()
        self.progressBar.setRange(0,err_cnt)
        
        errChecked["이름"] = "Unknown"
        errChecked["학번"] = "Unknown"
        
        k = 0
        for ia in errFnM["파일번호"]:
            locs = []
            errChecked.loc[errChecked["파일번호"] == f"{ia}",'이름'] = errFnM[errFnM["파일번호"]==f"{ia}"]["이름"].iloc[0]
            errChecked.loc[errChecked["파일번호"] == f"{ia}",'학번'] = errFnM[errFnM["파일번호"]==f"{ia}"]["학번"].iloc[0]
            name = errChecked[errChecked["파일번호"]==f"{ia}"]["이름"].iloc[0]
            serial = errChecked[errChecked["파일번호"]==f"{ia}"]["학번"].iloc[0]
            page = int(errChecked[errChecked["파일번호"]==f"{ia}"]["페이지"].iloc[0])-1
            
            for loc in errChecked.loc[errChecked["파일번호"] == f"{ia}"]["답안좌표"]:
                tmp = loc.replace(" ","").split(",")
                x = int(tmp[0])
                y = int(tmp[1])
                dT = [x,y]
                locs.append(dT)
            i=1
            for num in range(0,page):
                i += qus_num[num]
            print(len(answer_loc[page]))
            print(len(locs))
            
            if len(answer_loc[page]) == len(locs):
                self.txtBrowser.append(f"File #{ia} \nStudent Info : \n\tName : {name} \n\tSerial : {serial} \n\tPage : {page+1}")
                for a,b in zip(answer_loc[page],locs):
                    isCorrect = False
                    point = 0
                    if distance(a, b) < 15: 
                        self.txtBrowser.append(f"{i}번: 정답 {score_arr[i-1]}점")
                        point = int(score_arr[i-1])
                        isCorrect = True
                    else : 
                        self.txtBrowser.append(f"{i}번: 오답")
                    i += 1
                    errMsg = ""
                    if name == "Unknown":
                        errMsg = f"이름인식에 실패했습니다. File #{ia}"
                    data = pd.Series([name, serial, page+1, i, isCorrect, point,errMsg], index=columns)
                    df = df._append(data, ignore_index=True)
            else:
                print("err")
                data = pd.Series([name, serial, -1, -1, isCorrect, 0,f"문제수가 맞지않습니다.File #{ia}"], index=columns)
                df = df._append(data, ignore_index=True)
            
            
            self.txtBrowser.append("=======================")
            k+=1
            self.progressBar.setValue(k)
            
        self.labelProgress.setText("채점완료")
        self.txtBrowser.append("Done")
        df.to_excel('result_detail.xlsx', index=False)
        outdf, _avg, _min, _max, _std = output(df)
        self.txtBrowser.append(f"평균: {_avg}, 최저: {_min},최고: {_max}, 표준편차: {_std}")
        outdf.to_excel('result_summary.xlsx', index=False)


class Intro(QtWidgets.QMainWindow, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(QSize(625, 470))
        self.initUi()

        df = pd.read_csv("./pathList.csv", index_col = 0)
        self.create_table_widget(self.pathSaveList, df)
    
    def initUi(self):
        self.setWindowTitle("AutoScore")
        self.openAnswer.clicked.connect(self.openAns)
        self.openScanned.clicked.connect(self.openScn)
        self.introNextBtn.clicked.connect(self.introNext)
        self.saveBtn.clicked.connect(self.savePath)
        self.loadBtn.clicked.connect(self.loadPath)
    
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
        if scannedDir == "" or answerDir == "":
            self.introErrMsg.setStyleSheet("Color : red")
            self.introErrMsg.setText("폴더 경로를 입력해주세요")
        elif len(os.listdir(scannedDir)) < len(os.listdir(answerDir)):
            self.introErrMsg.setStyleSheet("Color : red")
            self.introErrMsg.setText("채점할 시험지 갯수가 적습니다. 파일경로를 확인해주세요")
        elif scannedDir == answerDir:
            self.introErrMsg.setStyleSheet("Color : red")
            self.introErrMsg.setText("두 폴더 경로가 같습니다.")
        else:
            self.introErrMsg.setStyleSheet("Color : green")
            self.introErrMsg.setText("정상")
            Window2 = AutoScoring()
            self.hide()
            Window2.runAutoScore()
    
    def savePath(self):
        name = self.saveText.text()
        if not name or not answerDir or not scannedDir:
            return  # 이름, answerDir, scannedDir 중 하나라도 없으면 아무것도 하지 않음

        existing_df = pd.read_csv("./pathList.csv")
        new_data = pd.DataFrame({'Name': [name], 'AnswerDir': [answerDir], 'ScannedDir': [scannedDir]})
        existing_df = pd.concat([existing_df, new_data])
        #existing_df = existing_df.append(new_data, ignore_index=True)
        #existing_df = existing_df[['Name', 'AnswerDir', 'ScannedDir']]
        existing_df.to_csv("./pathList.csv", index=False)
        self.pathSaveList.setRowCount(0)
        updated_df = pd.read_csv("./pathList.csv", index_col = 0)
        self.create_table_widget(self.pathSaveList, updated_df)

    def loadPath(self):
        global scannedDir, answerDir
        selected_row = self.pathSaveList.currentRow()
        answerDir = (self.pathSaveList.item(selected_row, 0).text())
        scannedDir = (self.pathSaveList.item(selected_row, 1).text())
        self.folderDirAnswer.setText(answerDir)
        fileList = os.listdir(answerDir)
        fileCount = len(fileList)
        self.countAnswerPage.setText(str(fileCount) + "개의 파일을 찾았습니다.")
        self.folderDirScanned.setText(scannedDir)
        fileList = os.listdir(scannedDir)
        fileCount = len(fileList)
        self.countScannedPage.setText(str(fileCount) + "개의 파일을 찾았습니다.")
        
    def create_table_widget(self, widget, df):
        widget.setRowCount(len(df.index))
        widget.setColumnCount(len(df.columns))
        widget.setHorizontalHeaderLabels(df.columns)

        df.index = df.index.astype(str)

        widget.setVerticalHeaderLabels(df.index)

        for row_index, row in enumerate(df.index):
            for col_index, column in enumerate(df.columns):
                value = df.loc[row][column]
                item = QTableWidgetItem(str(value))
                widget.setItem(row_index, col_index, item)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    intro = Intro()
    intro.show()
    app.exec_()