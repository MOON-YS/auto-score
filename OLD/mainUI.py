import sys
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, qApp, QAction
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets

class Lobby(QDialog):
    def __init__(self):
        super(Lobby,self).__init__()
        loadUi("ui/lobby.ui",self)
        self.btn_create_test.clicked.connect(self.gotoInfo)
        self.btn_quit.clicked.connect(qApp.exit)
        
    def gotoInfo(self):
        infoWindow = Info()
        widget.addWidget(infoWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        
class Info(QDialog):
    def __init__(self):
        super(Info,self).__init__()
        loadUi("ui/info.ui",self)
        self.btn_next.clicked.connect(self.gotoNext)
        self.btn_prev.clicked.connect(self.gotoPrev)
    
    def gotoPrev(self):
        widget.setCurrentIndex(widget.currentIndex()-1)
        
    def gotoNext(self):
        cqe = CheckQ()
        widget.addWidget(cqe)
        widget.setCurrentIndex(widget.currentIndex()+1)    
    
class CheckQ(QDialog):
    def __init__(self):
        super(CheckQ,self).__init__()
        loadUi("ui/check_question.ui",self)
        self.btn_next.clicked.connect(self.gotoNext)
        self.btn_prev.clicked.connect(self.gotoPrev)
        
    def gotoPrev(self):
        widget.setCurrentIndex(widget.currentIndex()-1)
    
    def gotoNext(self):
        res = ResultSc()
        widget.addWidget(res)
        widget.setCurrentIndex(widget.currentIndex()+1)  
        
class ResultSc(QMainWindow):
    def __init__(self):
        super(ResultSc,self).__init__()
        loadUi("ui/result.ui",self)
        self.btn_gotoLobby.clicked.connect(self.gotoLobby)
        self.actionSet_Grade.triggered.connect(self.openGrade)
        self.actionAnalyze.triggered.connect(self.openAnalyze)
        self.grade = SetGrade()
        self.analyze = UiAnalyze()

    def gotoLobby(self):
        widget.setCurrentIndex(0)
        
    def openGrade(self):
        self.hide()
        self.grade.show()
        self.grade.exec()
        self.show()
        
    def openAnalyze(self):
        self.hide()
        self.analyze.show()
        self.analyze.exec()
        self.show()
        
class SetGrade(QDialog):
    def __init__(self):
        super(SetGrade,self).__init__()
        loadUi("ui/resultGrade.ui",self)
        self.btn_close.clicked.connect(self.close)

class UiAnalyze(QDialog):
    def __init__(self):
        super(UiAnalyze,self).__init__()
        loadUi("ui/resultAnalyze.ui",self)
        self.btn_close.clicked.connect(self.close)
           
app = QApplication(sys.argv)
widget=QtWidgets.QStackedWidget()
lobby=Lobby()

widget.addWidget(lobby)
widget.setFixedHeight(720)
widget.setFixedWidth(1280)
widget.show()

try:
    sys.exit(app.exec_())
except:
    print("Exiting")