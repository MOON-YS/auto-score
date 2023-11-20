from PyQt5 import QtCore, QtGui, QtWidgets, uic
import os
import pandas as pd
from pathlib import Path
class PhotoViewer(QtWidgets.QGraphicsView):
    photoClicked = QtCore.pyqtSignal(QtCore.QPoint)
    def __init__(self, parent):
        super(PhotoViewer, self).__init__(parent)
        self._zoom = 0
        self._nowFile = 0
        self._pos = 0
        self._empty = True
        self._scene = QtWidgets.QGraphicsScene(self)
        self._photo = QtWidgets.QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)

    def hasPhoto(self):
        return not self._empty

    def fitInView(self, scale=True):
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.hasPhoto():
                unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.scale(factor, factor)
            self._zoom = 0

    def setPhoto(self, pixmap=None, nf=None):
        self._zoom = 0
        self._nowFile = nf
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
        else:
            self._empty = True
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self._photo.setPixmap(QtGui.QPixmap())
        self.fitInView()

    def wheelEvent(self, event):
        if self.hasPhoto():
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView()
            else:
                self._zoom = 0

    def toggleDragMode(self):
        if self.dragMode() == QtWidgets.QGraphicsView.ScrollHandDrag:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        elif not self._photo.pixmap().isNull():
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
    
    def mousePressEvent(self, event):
        if self._photo.isUnderMouse():
            self.photoClicked.emit(self.mapToScene(event.pos()).toPoint())
        super(PhotoViewer, self).mousePressEvent(event)

class QcWindow(QtWidgets.QWidget):
    
    def __init__(self):
        super(QcWindow, self).__init__()
        self.setWindowTitle("AutoScore")
        self.ui = uic.loadUi("QuestionCheck.ui",self)
        self.viewer = PhotoViewer(self)
        self.files = []
        self.nowPage = 0
        self.fileCount = 0
        self.toggled = True
        self.imgPath = ''
        self.answerData = ''
        
        #set next and previous button
        self.nextBtn.clicked.connect(self.nextImage)
        self.prevBtn.clicked.connect(self.previousImage)
        self.addRow.clicked.connect(self.addCellToTable)
        self.subRow.clicked.connect(self.subCellToTable)
        self.startScoring.clicked.connect(self.saveData)
        self.upRow.clicked.connect(self.upRowTable)
        self.downRow.clicked.connect(self.downRowTable)
        # Button to change from drag/pan to getting pixel info
        self.btnPixInfo.clicked.connect(self.pixInfo)
        self.qList.setRowCount(0)
        self.qList.setColumnCount(4)
        self.qList.setHorizontalHeaderLabels(["페이지","번호", "정답좌표","배점"])
        
        self.qList.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        # Arrange layout
        self.editPixInfo.setReadOnly(True)
        self.viewer.photoClicked.connect(self.photoClicked)
        
        self.verticalLayout_3.addWidget(self.viewer)
        
    
    def setQData(self, data):
        n = 0
        self.answerData = data
        for page,num,loc in zip(data["페이지"],data["번호"],data["정답좌표"]):
            self.qList.insertRow(n)
            self.qList.setItem(n,0,QtWidgets.QTableWidgetItem(str(page)))
            self.qList.setItem(n,1,QtWidgets.QTableWidgetItem(str(num)))
            self.qList.setItem(n,2,QtWidgets.QTableWidgetItem(str(loc)))
            n+=1
        
    def loadImage(self):
        fileList = os.listdir(self.imgPath)

        self.fileCount = len(fileList)
        self.files = fileList
        self.viewer.setPhoto(QtGui.QPixmap(self.imgPath+"/"+self.files[self.nowPage]),self.files[self.nowPage])
        self.Page.setText(f"1 / {self.fileCount}")
        

    def pixInfo(self):
        if not self.toggled:
            self.btnPixInfo.setStyleSheet("color: rgb(212, 212, 202);background-color: rgb(30, 30, 30);border: 2px solid rgb(212, 212, 202);")
        else :
            self.btnPixInfo.setStyleSheet("color: rgb(30, 30, 30);background-color: rgb(212, 212, 202);border: 2px solid rgb(212, 212, 202);")
        self.toggled = not self.toggled
        self.viewer.toggleDragMode()

    def photoClicked(self, pos):
        if self.viewer.dragMode()  == QtWidgets.QGraphicsView.NoDrag:
            self.editPixInfo.setText('%d, %d' % (pos.x(), pos.y()))
            
    def nextImage(self):
        if self.nowPage < len(self.files)-1:
            self.toggled = True
            self.btnPixInfo.setStyleSheet("color: rgb(212, 212, 202);background-color: rgb(30, 30, 30);border: 2px solid rgb(212, 212, 202);")
            self.nowPage +=1
            self.Page.setText(f"{self.nowPage+1} / {self.fileCount}")
            self.viewer.setPhoto(QtGui.QPixmap(self.imgPath+"/"+self.files[self.nowPage]),self.files[self.nowPage])
            
    def previousImage(self):
        if self.nowPage > 0:
            self.toggled = True
            self.btnPixInfo.setStyleSheet("color: rgb(212, 212, 202);background-color: rgb(30, 30, 30);border: 2px solid rgb(212, 212, 202);")
            self.nowPage -=1
            self.Page.setText(f"{self.nowPage+1} / {self.fileCount}")
            self.viewer.setPhoto(QtGui.QPixmap(self.imgPath+"/"+self.files[self.nowPage]),self.files[self.nowPage])
    
    def addCellToTable(self):
        self.qList.insertRow(self.qList.rowCount())
        
    def subCellToTable(self):
        for i in self.qList.selectedIndexes():
            self.qList.removeRow(i.row())
    
    def setImgPath(self, path):
        self.imgPath = os.path.abspath(path)
        self.loadImage()
    
    def saveData(self):
        len = self.qList.rowCount()
        newData = pd.DataFrame(columns=["페이지","번호","정답좌표","배점"])
        tmpPage = []
        tmpNum = []
        tmpLoc = []
        tmpPoint = []
        for i in range(0,len):
            if self.qList.item(i,3) == None: return
            if self.qList.item(i,2) == None: return
            if self.qList.item(i,1) == None: return
            if self.qList.item(i,0) == None: return
            tmpPage.append(self.qList.item(i,0).text())
            tmpNum.append(self.qList.item(i,1).text())
            tmpLoc.append(self.qList.item(i,2).text())
            tmpPoint.append(self.qList.item(i,3).text())
        newData["페이지"] = tmpPage
        newData["번호"] = tmpNum
        newData["정답좌표"] = tmpLoc
        newData["배점"] = tmpPoint

        self.answerData = newData
        self.close()
        
    def upRowTable(self):
        crnt = self.qList.selectedIndexes()[0].row()
        crntc = self.qList.selectedIndexes()[0].column()
        if crnt == 0 : return
        ccol = self.qList.columnCount()
        for i in range(0,ccol):
            lower = self.qList.item(crnt, i).text()
            upper = self.qList.item(crnt-1, i).text()
            self.qList.setItem(crnt-1,i,QtWidgets.QTableWidgetItem(str(lower)))
            self.qList.setItem(crnt,i,QtWidgets.QTableWidgetItem(str(upper)))
        self.qList.setCurrentCell(crnt-1, crntc)
        return
    
    def downRowTable(self):
        crnt = self.qList.selectedIndexes()[0].row()
        crntc = self.qList.selectedIndexes()[0].column()
        if crnt == self.qList.rowCount() : return
        ccol = self.qList.columnCount()
        for i in range(0,ccol):
            lower = self.qList.item(crnt, i).text()
            upper = self.qList.item(crnt+1, i).text()
            self.qList.setItem(crnt+1,i,QtWidgets.QTableWidgetItem(str(lower)))
            self.qList.setItem(crnt,i,QtWidgets.QTableWidgetItem(str(upper)))
        self.qList.setCurrentCell(crnt+1, crntc)
        return

#testing code
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = QcWindow()
    data = pd.read_csv('testTable.csv',encoding="cp949")
    window.setQData(data)
    window.setImgPath("./AnswerPage")
    window.show()
    sys.exit(app.exec_())
    