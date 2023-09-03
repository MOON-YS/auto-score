import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout,QSplitter,QFrame, QHBoxLayout, QVBoxLayout

from PyQt5.QtCore import Qt
class MyApp(QWidget):
    
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('My First Application')
        
        btn1 = QPushButton('&NEW TEST', self)
        btn2 = QPushButton('&LOAD TEST', self)
        quitBtn = QPushButton('&QUIT', self)
        grid = QGridLayout()
        
        top = QFrame()
        top.setFrameShape(QFrame.Box)
        
        midright = QFrame()
        midright.setFrameShape(QFrame.Panel)
        midc = QFrame()
        midc.setFrameShape(QFrame.Panel)
        left = QFrame()
        left.setFrameShape(QFrame.Panel)
        
        btnSet = QSplitter(Qt.Vertical)
        
        btnSet.addWidget(btn1)
        btnSet.addWidget(btn2)
        
        btnSet.addWidget(midc)
        TestList = QSplitter(Qt.Vertical)
        TestList.addWidget(top)

        quitBtn.setMaximumWidth(60)
        grid.addWidget(btnSet,0,1)
        grid.addWidget(TestList,0,0)
        grid.addWidget(quitBtn,1,2)

        self.setLayout(grid)
        self.setWindowTitle('QPushButton')
        self.setGeometry(300, 300, 1280, 720)
        self.show()

if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = MyApp()
   sys.exit(app.exec_())