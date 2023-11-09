from PyQt5 import QtCore, QtGui, QtWidgets, uic
import os
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

class Window(QtWidgets.QWidget):
    
    def __init__(self):
        super(Window, self).__init__()
        self.setWindowTitle("AutoScore")
        self.ui = uic.loadUi("imageShow.ui",self)
        self.viewer = PhotoViewer(self)
        self.files = []
        self.nowPage = 0
        self.fileCount = 0
        self.toggled = True
        
        #set next and previous button
        self.nextBtn.clicked.connect(self.nextImage)
        self.prevBtn.clicked.connect(self.previousImage)
        self.addPt.clicked.connect(self.addPtToList)
        self.subPt.clicked.connect(self.subPtFromList)
        # Button to change from drag/pan to getting pixel info
        self.btnPixInfo.clicked.connect(self.pixInfo)
        
        # Arrange layout
        self.editPixInfo.setReadOnly(True)
        self.viewer.photoClicked.connect(self.photoClicked)
        
        self.verticalLayout_3.addWidget(self.viewer)
        
        #'Load image' Automaticaly
        self.loadImage()

    def loadImage(self):
        fileList = os.listdir("./Err")
        self.fileCount = len(fileList)
        self.files = fileList
        self.Page.setText(f"1 / {self.fileCount}")
        self.viewer.setPhoto(QtGui.QPixmap("./Err/"+self.files[self.nowPage]),self.files[self.nowPage])

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
            self.viewer.setPhoto(QtGui.QPixmap("./Err/"+self.files[self.nowPage]),self.files[self.nowPage])
            
    def previousImage(self):
        if self.nowPage > 0:
            self.toggled = True
            self.btnPixInfo.setStyleSheet("color: rgb(212, 212, 202);background-color: rgb(30, 30, 30);border: 2px solid rgb(212, 212, 202);")
            self.nowPage -=1
            self.Page.setText(f"{self.nowPage+1} / {self.fileCount}")
            self.viewer.setPhoto(QtGui.QPixmap("./Err/"+self.files[self.nowPage]),self.files[self.nowPage])
    
    def addPtToList(self):
        text = str(self.viewer._nowFile) + " : " + str(self.editPixInfo.text())
        self.pointList.addItem(text)
        
    def subPtFromList(self):
        row = self.pointList.currentRow()
        self.pointList.takeItem(row)
        

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())