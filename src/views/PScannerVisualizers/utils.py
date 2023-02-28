import numpy as np
from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem
from PyQt6 import QtCore, QtGui
from OpenGL import GL
from PyQt6.QtGui import QColor
from typing import Union, Tuple
import pyqtgraph as pg


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


class Points3D(GLGraphicsItem):
    def __init__(
            self,
            points: np.ndarray,
            size: float,
            glOptions: dict,
            color: Union[str, QColor, Tuple[int, int, int, int]]):
        GLGraphicsItem.__init__(self)
        self.color: QColor = pg.mkColor(color)
        self.size = size
        self.points = points
        self.setGLOptions(glOptions)
        self.update()

    def paint(self):
        self.setupGLState()
        points = np.ascontiguousarray(self.points[:, [0, 1, 2]], dtype=np.float32)

        GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
        GL.glEnableClientState(GL.GL_COLOR_ARRAY)

        GL.glEnable(GL.GL_POINT_SMOOTH)
        GL.glPointSize(self.size)

        # first point
        GL.glColor4f(0, 1, 0, self.color.getRgbF()[-1])
        GL.glBegin(GL.GL_POINTS)
        GL.glVertex3f(points[0, 0], points[0, 1], points[0, 2])
        GL.glEnd()

        GL.glColor4f(*self.color.getRgbF())

        GL.glBegin(GL.GL_POINTS)
        for i in range(1, points.shape[0]-1):
            GL.glVertex3f(points[i, 0], points[i, 1], points[i, 2])
        GL.glEnd()

        # last point
        GL.glColor4f(1, 0, 0, self.color.getRgbF()[-1])
        GL.glBegin(GL.GL_POINTS)
        GL.glVertex3f(points[-1, 0], points[-1, 1], points[-1, 2])
        GL.glEnd()

        GL.glDisableClientState(GL.GL_COLOR_ARRAY)
        GL.glDisableClientState(GL.GL_VERTEX_ARRAY)

