import pyqtgraph.opengl as gl
import pyqtgraph as pg
import numpy as np
from stl import mesh
from src.scanner import BaseAxes
import os
from PyQt6 import QtCore, QtGui
from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem
from typing import Union


DEFAULT_SETTINGS = {
    'room_size': (3000, 3000, 5000, ),
    'scanner_zone_size': (2262.92, 2137.09, 531.4, ),
    'scanner_offset': (368.54, 300, 200, ),
    'scanner_L': (0, 0, 200, ),
}


def coords_to_GL_coords(func):
    def wrapper(self, x, y, z, w=None):
        if w is not None:
            return func(self, x=z, y=x, z=y, w=w)
        else:
            return func(self, x=z, y=x, z=y)
    return wrapper


def BaseAxes_to_GL_coords(func):
    def wrapper(_, axes: BaseAxes):
        return func(_, x=axes.z, y=axes.x, z=axes.y, w=axes.w)
    return wrapper


class TextItem(GLGraphicsItem):
    """Draws text in 3D."""

    def __init__(self, pos: list[int, int], text: str, font_size: int = 16, color=QtCore.Qt.GlobalColor.black):
        """All keyword arguments are passed to setData()"""
        GLGraphicsItem.__init__(self)
        self.pos = pos
        self.color = color
        self.text = text
        self.font_size = font_size
        self.font = QtGui.QFont('Helvetica', font_size)

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


class ScannerVisualizer(gl.GLViewWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_sizeX = 5000  # mm
        self.room_sizeY = 3000  # mm
        self.room_sizeZ = 3000  # mm

        self.scanner_zone_sizeX = 531.4
        self.scanner_zone_sizeY = 2262.92
        self.scanner_zone_sizeZ = 2137.09

        self.scanner_LX = 200
        self.scanner_LY = 0
        self.scanner_LZ = 0

        self.scanner_offsetX = 200
        self.scanner_offsetY = (self.room_sizeY - self.scanner_zone_sizeY) / 2
        self.scanner_offsetZ = 300

        points, faces = self._loadSTL(os.path.join(os.path.dirname(__file__), 'assets/cylinder.stl'))
        self.pillar_meshdata = gl.MeshData(vertexes=points, faces=faces)

        points, faces = self._loadSTL(os.path.join(os.path.dirname(__file__), 'assets/cylinder.stl'))
        self.point_meshdata = gl.MeshData(vertexes=points, faces=faces)

        self.setBackgroundColor(pg.mkColor('white'))

        self.opts['distance'] = 100*max([self.room_sizeX, self.room_sizeY, self.room_sizeZ])
        self.opts['fov'] = 1
        self.setGeometry(400, 400, 400, 400)
        self.pan(self.room_sizeX / 2, self.room_sizeY / 2, self.room_sizeZ / 2)

        self.scanner_pos = BaseAxes(0, 0, 0, 0)
        self.object_pos = BaseAxes(self.room_sizeX/2, self.room_sizeY/2, self.room_sizeZ/2)

        self.grid_items = self.draw_grid()
        self.scanner_zone_items = self.draw_scanner_zone()
        self.scanner_items = self.draw_scanner()
        self.object_items = self.draw_object()
        self.points_items = self.draw_points([], [], [], [])
        self.draw_text()

    @coords_to_GL_coords
    def set_room_size(self, x: float, y: float, z: float):
        """
        Set room sizes in meters

        :param x:
        :param y:
        :param z:
        :return:
        """
        self.room_sizeX, self.room_sizeY, self.room_sizeZ = x, y, z
        self.redraw_grid()

    @coords_to_GL_coords
    def set_scanner_zone_size(self, x: float, y: float, z: float):
        """
        Set scanner zone sizes in meters

        :param x:
        :param y:
        :param z:
        :return:
        """
        self.scanner_zone_sizeX, self.scanner_zone_sizeY, self.scanner_zone_sizeZ = x, y, z
        self.redraw_scanner_zone()

    @coords_to_GL_coords
    def set_offset(self, x: float, y: float, z: float):
        """
        Set scanner zone offset in meters

        :param x:
        :param y:
        :param z:
        :return:
        """
        self.scanner_offsetX, self.scanner_offsetY, self.scanner_offsetZ = x, y, z
        self.redraw_scanner_zone()
        self.redraw_scanner()

    @coords_to_GL_coords
    def set_scanner_L(self, x: float, y: float, z: float):
        self.scanner_LX, self.scanner_LY, self.scanner_LZ = x, y, z
        self.redraw_scanner_zone()
        self.redraw_scanner()

    def set_settings(
            self,
            room_size: tuple[float, float, float] = None,
            scanner_zone_size: tuple[float, float, float] = None,
            scanner_offset: tuple[float, float, float] = None,
            scanner_L: tuple[float, float, float] = None
    ):
        if room_size is not None:
            self.set_room_size(x=room_size[0], y=room_size[1], z=room_size[2])
        if scanner_zone_size is not None:
            self.set_scanner_zone_size(x=scanner_zone_size[0], y=scanner_zone_size[1], z=scanner_zone_size[2])
        if scanner_offset is not None:
            self.set_offset(x=scanner_offset[0], y=scanner_offset[1], z=scanner_offset[2])
        if scanner_L is not None:
            self.set_scanner_L(x=scanner_L[0], y=scanner_L[1], z=scanner_L[2])
        self.redraw_object()

    def set_settings_from_dict(self, settings: dict):
        self.set_settings(**settings)

    @BaseAxes_to_GL_coords
    def set_scanner_pos(self, x: float, y: float, z: float, w: float):
        self.scanner_pos = BaseAxes(x, y, z, w)
        self.redraw_scanner()

    @BaseAxes_to_GL_coords
    def set_object_pos(self, x: float, y: float, z: float, *args):
        self.object_pos = BaseAxes(x, y, z)
        self.redraw_object()

    def draw_grid(self):
        """
        Creates grid

        :return:
        """
        gx = gl.GLGridItem()
        gx.setColor('gray')
        gx.setSize(self.room_sizeZ, self.room_sizeY)
        gx.setSpacing(1000, 1000)
        gx.rotate(90, 0, -1, 0)
        gx.translate(0, self.room_sizeY / 2, self.room_sizeZ / 2)
        self.addItem(gx)

        gy = gl.GLGridItem()
        gy.setColor('gray')
        gy.setSize(self.room_sizeX, self.room_sizeZ)
        gy.setSpacing(1000, 1000)
        gy.rotate(90, 1, 0, 0)
        gy.translate(self.room_sizeX / 2, 0, self.room_sizeZ / 2)
        self.addItem(gy)

        gz = gl.GLGridItem()
        gz.setColor('gray')
        gz.setSize(self.room_sizeX, self.room_sizeY)
        gz.setSpacing(1000, 1000)
        gz.translate(self.room_sizeX / 2, self.room_sizeY / 2, 0)
        self.addItem(gz)

        return gx, gy, gz

    def redraw_grid(self):
        for item in self.grid_items:
            self.removeItem(item)
        self.grid_items = self.draw_grid()

    def draw_scanner_zone(self):
        """
        Creates

        :return:
        """
        color1 = pg.mkColor((0, 200, 0, 200))

        pts = [
            [0, self.scanner_offsetY + self.scanner_LY, self.scanner_offsetZ + self.scanner_LZ],
            [
                0,
                self.scanner_offsetY + self.scanner_LY,
                self.scanner_offsetZ + self.scanner_LZ + self.scanner_zone_sizeZ
            ],
            [
                0,
                self.scanner_offsetY + self.scanner_LY + self.scanner_zone_sizeY,
                self.scanner_offsetZ + self.scanner_LZ + self.scanner_zone_sizeZ
            ],
            [
                0,
                self.scanner_offsetY + self.scanner_LY + self.scanner_zone_sizeY,
                self.scanner_offsetZ + self.scanner_LZ
            ],
            [
                0,
                self.scanner_offsetY + self.scanner_LY,
                self.scanner_offsetZ + self.scanner_LZ
            ]
        ]

        zonex = gl.GLLinePlotItem(pos=pts, antialias=True, width=2, color=color1)
        self.addItem(zonex)

        pts = [
            [
                self.scanner_offsetX + self.scanner_LX,
                self.scanner_offsetY + self.scanner_LY,
                0
            ],
            [
                self.scanner_offsetX + self.scanner_LX + self.scanner_zone_sizeX,
                self.scanner_offsetY + self.scanner_LY,
                0
            ],
            [
                self.scanner_offsetX + self.scanner_LX + self.scanner_zone_sizeX,
                self.scanner_offsetY + self.scanner_LY + self.scanner_zone_sizeY,
                0
            ],
            [
                self.scanner_offsetX + self.scanner_LX,
                self.scanner_offsetY + self.scanner_LY + self.scanner_zone_sizeY,
                0
            ],
            [
                self.scanner_offsetX + self.scanner_LX,
                self.scanner_offsetY + self.scanner_LY,
                0
            ]
        ]

        zonez = gl.GLLinePlotItem(pos=pts, antialias=True, width=2, color=color1)
        self.addItem(zonez)

        return zonex, zonez

    def redraw_scanner_zone(self):
        for item in self.scanner_zone_items:
            self.removeItem(item)
        self.scanner_zone_items = self.draw_scanner_zone()

    def draw_scanner(self):
        color1 = pg.mkColor((200, 0, 0, 200))
        color2 = pg.mkColor((0, 0, 200, 200))
        pts = [
            [
                0,
                self.scanner_offsetY + self.scanner_pos.y,
                self.scanner_offsetZ + self.scanner_pos.z
            ],
            [
                self.scanner_offsetX + self.scanner_pos.x,
                self.scanner_offsetY + self.scanner_pos.y,
                self.scanner_offsetZ + self.scanner_pos.z
            ]
        ]
        linex = gl.GLLinePlotItem(pos=pts, antialias=True, width=3, color=color1)
        self.addItem(linex)

        pts = [
            [0, 0, self.scanner_offsetZ + self.scanner_pos.z],
            [0, self.scanner_offsetY + self.scanner_pos.y, self.scanner_offsetZ + self.scanner_pos.z]
        ]
        liney = gl.GLLinePlotItem(pos=pts, antialias=True, width=2, color=color1)
        self.addItem(liney)

        pts = [
            [0, self.scanner_offsetY + self.scanner_pos.y, 0],
            [0, self.scanner_offsetY + self.scanner_pos.y, self.scanner_offsetZ + self.scanner_pos.z]
        ]
        linez = gl.GLLinePlotItem(pos=pts, antialias=True, width=2, color=color1)
        self.addItem(linez)

        pts = [
            [
                self.scanner_offsetX + self.scanner_pos.x,
                self.scanner_offsetY + self.scanner_pos.y,
                self.scanner_offsetZ + self.scanner_pos.z
            ],
            [
                self.scanner_offsetX + self.scanner_pos.x + self.scanner_LX,
                self.scanner_offsetY + self.scanner_pos.y + self.scanner_LY,
                self.scanner_offsetZ + self.scanner_pos.z + self.scanner_LZ
            ],
        ]
        lineL = gl.GLLinePlotItem(pos=pts, antialias=True, width=2, color=color2)
        self.addItem(lineL)

        pts = [
            [self.object_pos.x, self.object_pos.y, 0],
            [self.object_pos.x-500*np.cos(self.scanner_pos.w), self.object_pos.y-500*np.sin(self.scanner_pos.w), 0]
        ]
        linew = gl.GLLinePlotItem(pos=pts, antialias=True, width=2, color=color2)
        self.addItem(linew)

        texts = [
            TextItem([5, 5], f'x={self.scanner_pos.y}'),
            TextItem([5, 5+1*16], f'y={self.scanner_pos.z}[mm]'),
            TextItem([5, 5+2*16], f'z={self.scanner_pos.x}[mm]'),
            TextItem([5, 5+3*16], f'w={self.scanner_pos.w}[mm]')
        ]
        for text in texts:
            self.addItem(text)

        return [linex, liney, linez, linew, lineL, *texts]

    def redraw_scanner(self):
        for item in self.scanner_items:
            self.removeItem(item)
        self.scanner_items = self.draw_scanner()

    def draw_object(self):
        object_pillar = gl.GLMeshItem(
            meshdata=self.pillar_meshdata,
            smooth=True,
            drawFaces=True,
            color=pg.mkColor((100, 100, 100, 100)),
            glOptions='opaque',  # translucent, opaque, additive
        )
        tt = np.eye(4)
        tt[3, 3] = 1
        tt[0, 0] = 300
        tt[1, 1] = 300
        tt[2, 2] = 10 * self.object_pos.z
        tt[0, 3] = self.object_pos.x
        tt[1, 3] = self.object_pos.y
        tr = pg.Transform3D(tt)
        object_pillar.applyTransform(tr, False)
        self.addItem(object_pillar)
        return object_pillar,

    def redraw_object(self):
        for item in self.object_items:
            self.removeItem(item)
        self.object_items = self.draw_object()

    def draw_text(self):
        color1 = pg.mkColor((50, 50, 50, 200))
        x = gl.GLTextItem(pos=[self.room_sizeX + 0.2, 0, 0], text='z', color=color1)
        self.addItem(x)
        y = gl.GLTextItem(pos=[0, self.room_sizeY + 0.2, 0], text='x', color=color1)
        self.addItem(y)
        z = gl.GLTextItem(pos=[0, 0, self.room_sizeZ + 0.1], text='y', color=color1)
        self.addItem(z)

    @staticmethod
    def _loadSTL(filename):
        m = mesh.Mesh.from_file(filename)
        points = m.points.reshape(-1, 3)
        faces = np.arange(points.shape[0]).reshape(-1, 3)
        return points, faces

    def draw_points(
            self,
            x: Union[list, np.array],
            y: Union[list, np.array],
            z: Union[list, np.array],
            w: Union[list, np.array]
    ):
        assert len(x) == len(y) == len(z) == len(w)
        objects = []
        for i in range(len(x)):
            object_point = gl.GLMeshItem(
                meshdata=self.point_meshdata,
                smooth=True,
                drawFaces=True,
                color=pg.mkColor((100, 100, 255, 100)),
                glOptions='opaque',  # translucent, opaque, additive
            )
            tt = np.eye(4)
            tt[3, 3] = 1
            tt[0, 0] = 100
            tt[1, 1] = 100
            tt[2, 2] = 1000
            tt[2, 3] = - 50 + z[i]
            tt[1, 3] = y[i]
            tt[0, 3] = x[i]
            tr = pg.Transform3D(tt)
            object_point.applyTransform(tr, True)
            objects.append(object_point)
            self.addItem(object_point)
        return objects

    @coords_to_GL_coords
    def set_points(
            self,
            x: Union[list, np.array],
            y: Union[list, np.array],
            z: Union[list, np.array],
            w: Union[list, np.array]
    ):
        for item in self.points_items:
            self.removeItem(item)
        self.points_items = self.draw_points(x, y, z, w)
