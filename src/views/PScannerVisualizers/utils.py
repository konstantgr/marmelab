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
        self.points = np.ascontiguousarray(points, dtype=np.float32)
        self.setGLOptions(glOptions)
        self.update()

    def paint(self):
        self.setupGLState()

        GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
        try:
            GL.glVertexPointerf(self.points)

            # GL.glEnable(GL.GL_POINT_SMOOTH)
            GL.glEnable(GL.GL_PROGRAM_POINT_SIZE)
            GL.glColor4f(*self.color.getRgbF())
            GL.glPointSize(self.size)

            with point_shader:
                GL.glDrawArrays(GL.GL_POINTS, 0, self.points.shape[0])

        finally:
            GL.glDisableClientState(GL.GL_COLOR_ARRAY)
            GL.glDisableClientState(GL.GL_VERTEX_ARRAY)


# Own shader
lights_shader = pg.opengl.shaders.ShaderProgram('light_shader', [
    pg.opengl.shaders.VertexShader("""
        varying vec3 normal;
        varying vec4 pos;
        void main() {
            // compute here for use in fragment shader
            normal = normalize(gl_NormalMatrix * gl_Normal);
            gl_FrontColor = gl_Color;
            gl_BackColor = gl_Color;
            gl_Position = ftransform();
            pos = gl_Vertex;
        }
    """),
    pg.opengl.shaders.FragmentShader("""
        varying vec3 normal;
        varying vec4 pos;
        void main() {
            vec3 lightSource = gl_NormalMatrix * vec3(10000.0, 10000.0, 10000.0);
            vec3 lightVector = normalize(lightSource - pos.xyz);
            float diff = max(dot(normal, lightVector), 0.0);
            vec4 color = gl_Color;
            color.x = color.x * (0.6 + 0.4*diff);
            color.y = color.y * (0.6 + 0.4*diff);
            color.z = color.z * (0.6 + 0.4*diff);
            gl_FragColor = color;
        }
    """)
])

# Shader for size changing point
point_shader = pg.opengl.shaders.ShaderProgram('point_shader', [
    pg.opengl.shaders.VertexShader("""
        varying vec3 normal;
        varying vec4 pos;
        void main() {
            // compute here for use in fragment shader
            normal = normalize(gl_NormalMatrix * gl_Normal);
            gl_FrontColor = gl_Color;
            gl_BackColor = gl_Color;
            gl_Position = ftransform();
            pos = gl_Vertex;
            gl_PointSize = 500000.0/gl_Position.w;
        }
    """),
    pg.opengl.shaders.FragmentShader("""
        varying vec3 normal;
        varying vec4 pos;
        void main() {
            vec3 lightSource = gl_NormalMatrix * vec3(10000.0, 10000.0, 10000.0);
            vec3 lightVector = normalize(lightSource - pos.xyz);
            float diff = max(dot(normal, lightVector), 0.0);
            vec4 color = gl_Color;
            color.x = color.x * (0.6 + 0.4*diff);
            color.y = color.y * (0.6 + 0.4*diff);
            color.z = color.z * (0.6 + 0.4*diff);
            gl_FragColor = color;
        }
    """)
])

