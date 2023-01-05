import pyqtgraph.opengl as gl
import pyqtgraph as pg
import numpy as np
from stl import mesh
from ...scanner import BaseAxes
from ..Project import PScanner, PScannerVisualizer, PWidget, PStorage, PScannerSignals
import os
from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import QWidget, QTextEdit
from pyqtgraph.opengl.GLGraphicsItem import GLGraphicsItem
from ..PObjects import Object3d
from ..PPaths import Path3d
from ..Widgets import SettingsTableWidget
from ..Variable import Setting, Unit
from OpenGL.GL import GL_BLEND, GL_DEPTH_TEST, GL_ALPHA_TEST, GL_CULL_FACE, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA
from ..icons import settings_icon


_DEFAULT_SETTINGS = [
    Setting(
        name='room_size_x',
        unit=Unit(m=1),
        description='',
        default_value=3000,
    ),
    Setting(
        name='room_size_y',
        unit=Unit(m=1),
        description='',
        default_value=3000,
    ),
    Setting(
        name='room_size_z',
        unit=Unit(m=1),
        description='',
        default_value=5000,
    ),
    Setting(
        name='scanner_zone_size_x',
        unit=Unit(m=1),
        description='',
        default_value=2262.92,
    ),
    Setting(
        name='scanner_zone_size_y',
        unit=Unit(m=1),
        description='',
        default_value=2137.09,
    ),
    Setting(
        name='scanner_zone_size_z',
        unit=Unit(m=1),
        description='',
        default_value=531.4,
    ),
    Setting(
        name='scanner_offset_x',
        unit=Unit(m=1),
        description='',
        default_value=368.54,
    ),
    Setting(
        name='scanner_offset_y',
        unit=Unit(m=1),
        description='',
        default_value=300,
    ),
    Setting(
        name='scanner_offset_z',
        unit=Unit(m=1),
        description='',
        default_value=200,
    ),
    Setting(
        name='scanner_L_x',
        unit=Unit(m=1),
        description='',
        default_value=0,
    ),
    Setting(
        name='scanner_L_y',
        unit=Unit(m=1),
        description='',
        default_value=0,
    ),
    Setting(
        name='scanner_L_z',
        unit=Unit(m=1),
        description='',
        default_value=200,
    ),

]

DEFAULT_SETTINGS = {setting.name: setting.default_value for setting in _DEFAULT_SETTINGS}


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


class ScannerVisualizer(gl.GLViewWidget):
    def __init__(
            self,
            scanner_signals: PScannerSignals,
            objects: PStorage,
            paths: PStorage,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.scanner_signals = scanner_signals
        self.objects = objects
        self.paths = paths

        self.room_sizeX, self.room_sizeY, self.room_sizeZ = 5000, 3000, 3000  # mm
        self.scanner_zone_sizeX, self.scanner_zone_sizeY, self.scanner_zone_sizeZ = 531.4, 2262.92, 2137.09
        self.scanner_LX, self.scanner_LY, self.scanner_LZ = 200, 0, 0
        self.scanner_offsetX, self.scanner_offsetZ = 200, 300
        self.scanner_offsetY = (self.room_sizeY - self.scanner_zone_sizeY) / 2

        points, faces = self._loadSTL(os.path.join(os.path.dirname(__file__), 'assets/cube.stl'))
        self.point_meshdata = gl.MeshData(vertexes=points, faces=faces)

        self.setBackgroundColor(pg.mkColor('white'))

        self.opts['distance'] = 100*max([self.room_sizeX, self.room_sizeY, self.room_sizeZ])
        self.opts['fov'] = 1
        self.setGeometry(400, 400, 400, 400)
        self.pan(self.room_sizeX / 2, self.room_sizeY / 2, self.room_sizeZ / 2)

        self.scanner_pos = BaseAxes(0, 0, 0, 0)

        self.grid_items = self.draw_grid()
        self.scanner_zone_items = self.draw_scanner_zone()
        self.scanner_items = self.draw_scanner()
        self.object_items = self.draw_objects()
        self.paths_items = self.draw_points()

        self.scanner_signals.position.connect(self.set_scanner_pos)
        self.objects.signals.changed.connect(self.redraw_objects)
        self.paths.signals.changed.connect(self.redraw_paths)
        # self.objects.signals.element_changed.connect(self.redraw_objects)
        # self.paths.signals.element_changed.connect(self.redraw_paths)

    @coords_to_GL_coords
    def set_room_size(self, x: float, y: float, z: float):
        """
        Set room sizes in meters

        :param x:
        :param y:
        :param z:
        :return:
        """
        if x is not None:
            self.room_sizeX = x
        if y is not None:
            self.room_sizeY = y
        if z is not None:
            self.room_sizeZ = z
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
        if x is not None:
            self.scanner_zone_sizeX = x
        if y is not None:
            self.scanner_zone_sizeY = y
        if z is not None:
            self.scanner_zone_sizeZ = z
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
        if x is not None:
            self.scanner_offsetX = x
        if y is not None:
            self.scanner_offsetY = y
        if z is not None:
            self.scanner_offsetZ = z
        self.redraw_scanner_zone()
        self.redraw_scanner()

    @coords_to_GL_coords
    def set_scanner_L(self, x: float, y: float, z: float):
        if x is not None:
            self.scanner_LX = x
        if y is not None:
            self.scanner_LY = y
        if z is not None:
            self.scanner_LZ = z
        self.redraw_scanner_zone()
        self.redraw_scanner()

    def set_settings(
            self,
            room_size_x: float = None,
            room_size_y: float = None,
            room_size_z: float = None,
            scanner_zone_size_x: float = None,
            scanner_zone_size_y: float = None,
            scanner_zone_size_z: float = None,
            scanner_offset_x: float = None,
            scanner_offset_y: float = None,
            scanner_offset_z: float = None,
            scanner_L_x: float = None,
            scanner_L_y: float = None,
            scanner_L_z: float = None
    ):
        self.set_room_size(x=room_size_x, y=room_size_y, z=room_size_z)
        self.set_scanner_zone_size(x=scanner_zone_size_x, y=scanner_zone_size_y, z=scanner_zone_size_z)
        self.set_offset(x=scanner_offset_x, y=scanner_offset_y, z=scanner_offset_z)
        self.set_scanner_L(x=scanner_L_x, y=scanner_L_y, z=scanner_L_z)
        self.redraw_objects()

    @BaseAxes_to_GL_coords
    def set_scanner_pos(self, x: float, y: float, z: float, w: float):
        self.scanner_pos = BaseAxes(x, y, z, w)
        self.redraw_scanner()

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

        x, y, z = self.draw_text()

        return gx, gy, gz, x, y, z

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

        texts = [
            TextItem([5, 5], f'x = {self.scanner_pos.y} [mm]', font_size=12),
            TextItem([5, 5+1*16], f'y = {self.scanner_pos.z} [mm]', font_size=12),
            TextItem([5, 5+2*16], f'z = {self.scanner_pos.x} [mm]', font_size=12),
            TextItem([5, 5+3*16], f'w = {self.scanner_pos.w} [rad]', font_size=12)
        ]
        for text in texts:
            self.addItem(text)

        if len(self.objects.data) >= 1:
            obj = self.objects.data[0]  # type: Object3d
            tr = obj.transformation
            pts = [
                [tr[0, 3], tr[1, 3], 0],
                [tr[0, 3]-500*np.cos(self.scanner_pos.w), tr[1, 3]-500*np.sin(self.scanner_pos.w), 0]
            ]
            linew = gl.GLLinePlotItem(pos=pts, antialias=True, width=2, color=color2)
            self.addItem(linew)
            return [linex, liney, linez, linew, lineL, *texts]
        return [linex, liney, linez, lineL, *texts]

    def redraw_scanner(self):
        for item in self.scanner_items:
            self.removeItem(item)
        self.scanner_items = self.draw_scanner()

    def draw_objects(self):
        objects_items = []
        for obj in self.objects.data:
            points = obj.mesh.points.reshape(-1, 3)
            faces = np.arange(points.shape[0]).reshape(-1, 3)
            item = gl.GLMeshItem(
                meshdata=gl.MeshData(vertexes=points, faces=faces),
                smooth=True,
                drawFaces=True,
                drawEdges=False,
                color=pg.mkColor((100, 100, 100, 200)),
                glOptions={
                    GL_DEPTH_TEST: True,
                    GL_BLEND: True,
                    GL_ALPHA_TEST: True,
                    GL_CULL_FACE: True,
                    'glBlendFunc': (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA),
                },  # or use one of str: translucent, opaque, additive
            )
            tr = pg.Transform3D(obj.transformation)
            item.applyTransform(tr, False)
            self.addItem(item)
            objects_items.append(item)
        return objects_items

    def redraw_objects(self):
        for item in self.object_items:
            self.removeItem(item)
        self.object_items = self.draw_objects()

    def draw_text(self):
        color1 = pg.mkColor((50, 50, 50, 200))
        x = gl.GLTextItem(pos=[self.room_sizeX + 0.2, 0, 0], text='z', color=color1)
        self.addItem(x)
        y = gl.GLTextItem(pos=[0, self.room_sizeY + 0.2, 0], text='x', color=color1)
        self.addItem(y)
        z = gl.GLTextItem(pos=[0, 0, self.room_sizeZ + 0.1], text='y', color=color1)
        self.addItem(z)
        return x, y, z

    @staticmethod
    def _loadSTL(filename):
        m = mesh.Mesh.from_file(filename)
        points = m.points.reshape(-1, 3)
        faces = np.arange(points.shape[0]).reshape(-1, 3)
        return points, faces

    def draw_points(self):
        paths_items = []
        for path in self.paths.data:  # type: Path3d
            for i in range(path.points.shape[0]):
                path_item = gl.GLMeshItem(
                    meshdata=self.point_meshdata,
                    smooth=True,
                    drawFaces=True,
                    color=pg.mkColor((100, 100, 255, 150)),
                    glOptions={
                        GL_DEPTH_TEST: True,
                        GL_BLEND: True,
                        GL_ALPHA_TEST: True,
                        GL_CULL_FACE: True,
                        'glBlendFunc': (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA),
                    },  # or use one of str: translucent, opaque, additive
                )
                tt = np.eye(4)
                tt[0, 0] = 1000 / 30
                tt[1, 1] = 1000 / 30
                tt[2, 2] = 1000 / 30
                tt[0, 3] = path.points[i, 2] + self.scanner_offsetX + self.scanner_LX
                tt[1, 3] = path.points[i, 0] + self.scanner_offsetX + self.scanner_LX
                tt[2, 3] = path.points[i, 1] + self.scanner_offsetY + self.scanner_LY
                tr = pg.Transform3D(tt)
                path_item.applyTransform(tr, False)
                paths_items.append(path_item)
                self.addItem(path_item)
        return paths_items

    def redraw_paths(self):
        for item in self.paths_items:
            self.removeItem(item)
        self.paths_items = self.draw_points()


class Settings(SettingsTableWidget):
    def __init__(self, visualizer: ScannerVisualizer):
        super(Settings, self).__init__(settings=_DEFAULT_SETTINGS)
        self.visualizer = visualizer

    def apply(self):
        self.visualizer.set_settings(**self.table.to_dict())


class PScannerVisualizer3D(PScannerVisualizer):
    def __init__(
            self, *args, objects: PStorage, paths: PStorage, **kwargs
    ):
        super(PScannerVisualizer3D, self).__init__(*args, **kwargs)
        self._widget = ScannerVisualizer(
            scanner_signals=self.scanner.signals,
            paths=paths,
            objects=objects
        )
        self._control_widgets = [
            PWidget(
                'Settings',
                Settings(visualizer=self._widget),
                icon=settings_icon
            )
        ]

    @property
    def widget(self) -> QWidget:
        return self._widget

    @property
    def control_widgets(self) -> list[PWidget]:
        return self._control_widgets
