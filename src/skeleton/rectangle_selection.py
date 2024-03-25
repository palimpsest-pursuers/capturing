from PyQt5.QtWidgets import QGraphicsObject, QWidget, QStyleOptionGraphicsItem
from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import QPainter, QBrush, QColor, QPen
import typing 

'''
Rectangle Selection Graphics for Cropping and Manual Calibration
Copied from MISHA Processing Software by Eric Gao
Written by Mallory Bridge
'''
class RectangleSelectView(QGraphicsObject):
    def __init__(self, scene, originalImage):
        super(RectangleSelectView, self).__init__()
        self.begin = QPointF()
        self.end = QPointF()
        self.my_scene = scene
        self.boundingRectScene = scene.sceneRect()
        self.scalex = originalImage.shape[0] / self.boundingRect().height()
        self.scaley = originalImage.shape[1] / self.boundingRect().width()

    def boundingRect(self):
        return self.boundingRectScene
    
    def paint(self, painter: QPainter, option: "QStyleOptionGraphicsItem", widget: typing.Optional[QWidget] = ...) -> None:
        br = QBrush(QColor(1, 130, 170, 85))
        painter.setBrush(br)
        pen = QPen()
        pen.setJoinStyle(Qt.MiterJoin)
        painter.setPen(pen)
        painter.drawRect(QRectF(self.begin, self.end))

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = event.pos()
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.end = event.pos()
        self.update()

    def getSelectedArea(self):
        return ([(self._convertPoint(self.begin.x(), self.scalex), 
                    self._convertPoint(self.begin.y(), self.scaley)), 
                    (self._convertPoint(self.end.x(), self.scalex),
                    self._convertPoint(self.end.y(), self.scaley))
                    ])
    
    def _convertPoint(self, point, scale_factor):
        return int(round(point * scale_factor))