from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem
from PyQt6 import QtCore, QtGui


class TextItem(GLGraphicsItem):
    """Draws text in 3D"""

    def __init__(self, pos: list[int, int], text: str, font_size: int = 16, color=QtCore.Qt.GlobalColor.black):
        """All keyword arguments are passed to setData()"""
        GLGraphicsItem.__init__(self)
        self.pos = pos
        self.color = color
        self.text = text
        self.font_size = font_size
        self.font = QtGui.QFont('Arial', font_size)

    def paint(self):
        if len(self.text) < 1:
            return
        self.setupGLState()

        painter = QtGui.QPainter(self.view())
        painter.setPen(self.color)
        painter.setFont(self.font)
        painter.setRenderHints(QtGui.QPainter.RenderHint.Antialiasing | QtGui.QPainter.RenderHint.TextAntialiasing)
        painter.drawText(self.pos[0], self.pos[1]+self.font_size, self.text)
        painter.end()