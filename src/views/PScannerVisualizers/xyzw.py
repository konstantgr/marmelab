import OpenGL.GL

from ..Widgets import SettingsTableWidget
from ...project.PVisualizers.xyzw_model import xyzwScannerVisualizer
from ..View import BaseView, QWidgetType
from PyQt6.QtWidgets import QSplitter, QVBoxLayout, QTabWidget
from PyQt6.QtCore import Qt
import pyqtgraph.opengl as gl
import pyqtgraph as pg
import numpy as np
from stl import mesh
from ...scanner import BaseAxes
from ...project.Project import PPath
import os
import OpenGL.GL as GL
from PyQt6.QtWidgets import QWidget
from OpenGL.GL import GL_BLEND, GL_DEPTH_TEST, GL_ALPHA_TEST, GL_CULL_FACE, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA
from .utils import TextItem, Points3D, lights_shader

import logging
logger = logging.getLogger()


def coords_to_GL_coords(x, y, z, w=None):
    """Перевод из координат сканера в координаты OpenGL"""
    if w is not None:
        return z, x, y, w
    else:
        return z, x, y


class Widget(gl.GLViewWidget):
    def __init__(
            self,
            model: xyzwScannerVisualizer,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.model = model
        self.scanner_signals = model.scanner.signals
        self.objects = model.objects
        self.paths = model.paths

        self.room_sizeX, self.room_sizeY, self.room_sizeZ = 5000, 3000, 3000  # mm
        self.scanner_zone_sizeX, self.scanner_zone_sizeY, self.scanner_zone_sizeZ = 531.4, 2262.92, 2137.09
        self.scanner_LX, self.scanner_LY, self.scanner_LZ = 200, 0, 0
        self.scanner_offsetX, self.scanner_offsetZ = 200, 300
        self.scanner_offsetY = (self.room_sizeY - self.scanner_zone_sizeY) / 2

        self.pillar_x = 4000
        self.pillar_y = self.room_sizeY/2
        self.pillar_z = 0
        self.pillar_h = 1000
        self.pillar_r = 100
        points, faces = self._loadSTL(os.path.join(os.path.dirname(__file__), 'assets/cylinder.stl'))
        self.pillar_meshdata = gl.MeshData(vertexes=points, faces=faces)

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
        self.connected_paths = []
        self.paths_items = self.draw_points()

        self.scanner_signals.position.connect(self.set_scanner_pos)
        self.objects.signals.changed.connect(self.redraw_objects)
        self.paths.signals.changed.connect(self.redraw_paths)
        self.model.signals.settings_updated.connect(self.settings_updated)
        
        self.settings_updated()

    def set_room_size(self, x: float, y: float, z: float):
        """
        Set room sizes in meters

        :param x:
        :param y:
        :param z:
        :return:
        """
        x, y, z = coords_to_GL_coords(x, y, z)
        if x is not None:
            self.room_sizeX = x
        if y is not None:
            self.room_sizeY = y
        if z is not None:
            self.room_sizeZ = z

    def set_scanner_zone_size(self, x: float, y: float, z: float):
        """
        Set scanner zone sizes in meters

        :param x:
        :param y:
        :param z:
        :return:
        """
        x, y, z = coords_to_GL_coords(x, y, z)
        if x is not None:
            self.scanner_zone_sizeX = x
        if y is not None:
            self.scanner_zone_sizeY = y
        if z is not None:
            self.scanner_zone_sizeZ = z

    def set_offset(self, x: float, y: float, z: float):
        """
        Set scanner zone offset in meters

        :param x:
        :param y:
        :param z:
        :return:
        """
        x, y, z = coords_to_GL_coords(x, y, z)
        if x is not None:
            self.scanner_offsetX = x
        if y is not None:
            self.scanner_offsetY = y
        if z is not None:
            self.scanner_offsetZ = z

    def set_scanner_L(self, x: float, y: float, z: float):
        x, y, z = coords_to_GL_coords(x, y, z)
        if x is not None:
            self.scanner_LX = x
        if y is not None:
            self.scanner_LY = y
        if z is not None:
            self.scanner_LZ = z

    def set_pillar(self, x: float, y: float, z: float, r: float, h: float):
        x, y, z = coords_to_GL_coords(x, y, z)
        if x is not None:
            self.pillar_x = x
        if y is not None:
            self.pillar_y = y
        if z is not None:
            self.pillar_z = z
        if h is not None:
            self.pillar_h = h
        if r is not None:
            self.pillar_r = r

    def settings_updated(self):
        self.set_settings(**self.model.settings)

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
            scanner_L_z: float = None,
            pillar_x: float = None,
            pillar_y: float = None,
            pillar_z: float = None,
            pillar_r: float = None,
            pillar_h: float = None,
    ):
        self.set_room_size(x=room_size_x, y=room_size_y, z=room_size_z)
        self.set_scanner_zone_size(x=scanner_zone_size_x, y=scanner_zone_size_y, z=scanner_zone_size_z)
        self.set_offset(x=scanner_offset_x, y=scanner_offset_y, z=scanner_offset_z)
        self.set_scanner_L(x=scanner_L_x, y=scanner_L_y, z=scanner_L_z)
        self.set_pillar(x=pillar_x, y=pillar_y, z=pillar_z, r=pillar_r, h=pillar_h)
        self.redraw_grid()
        self.redraw_scanner_zone()
        self.redraw_scanner()
        self.redraw_objects()
        self.redraw_paths()

    def set_scanner_pos(self, axes: BaseAxes):
        self.scanner_pos = BaseAxes(axes.z, axes.x, axes.y, axes.w)
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

    def pillar_transformation(self) -> np.ndarray:
        res = np.eye(4)
        res[0, 0] = res[1, 1] = self.pillar_r * 2
        res[2, 2] = self.pillar_h
        res[0, 3] = self.pillar_x
        res[1, 3] = self.pillar_y
        res[2, 3] = self.pillar_z + self.pillar_h/2
        return res

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

        tr = self.pillar_transformation()
        pts = [
            [tr[0, 3], tr[1, 3], 0],
            [tr[0, 3]-500*np.cos(self.scanner_pos.w), tr[1, 3]-500*np.sin(self.scanner_pos.w), 0]
        ]
        linew = gl.GLLinePlotItem(pos=pts, antialias=True, width=2, color=color2)
        self.addItem(linew)
        pillar = gl.GLMeshItem(
            meshdata=self.pillar_meshdata,
            smooth=True,
            drawFaces=True,
            drawEdges=False,
            color=pg.mkColor((120, 120, 120, 200)),
            shader=lights_shader,
            glOptions={
                GL_DEPTH_TEST: True,
                GL_BLEND: True,
                GL_ALPHA_TEST: True,
                GL_CULL_FACE: True,
                'glBlendFunc': (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA),
            },  # or use one of str: translucent, opaque, additive
        )
        tr = pg.Transform3D(self.pillar_transformation())
        pillar.applyTransform(tr, False)
        self.addItem(pillar)

        return [linex, liney, linez, linew, lineL, pillar, *texts]

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
        for path in self.paths.data:  # type: PPath

            if path.name not in self.connected_paths:
                path.signals.display_changed.connect(self.redraw_paths)
                self.connected_paths.append(path.name)
                
            points = path.get_points_ndarray()
            points_in_gl = np.zeros_like(points)
            x, y, z = coords_to_GL_coords(points[:, 0], points[:, 1], points[:, 2])
            points_in_gl[:, 0] = x + self.scanner_offsetX + self.scanner_LX
            points_in_gl[:, 1] = y + self.scanner_offsetY + self.scanner_LY
            points_in_gl[:, 2] = z + self.scanner_offsetZ + self.scanner_LZ

            item = Points3D(
                points=points_in_gl,
                color=pg.mkColor((100, 100, 255, 200)),
                size=8,
                glOptions={
                    GL_DEPTH_TEST: True,
                    GL_BLEND: True,
                    GL_ALPHA_TEST: True,
                    GL_CULL_FACE: True,
                    'glBlendFunc': (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA),
                },
            )
            paths_items.append(item)
            self.addItem(item)

            item = gl.GLLinePlotItem(
                pos=points_in_gl[:, [0, 1, 2]],
                color=pg.mkColor((80, 120, 255, 200)),
                width=1,
                antialias=True,
                glOptions={
                    GL_DEPTH_TEST: True,
                    GL_BLEND: True,
                    GL_ALPHA_TEST: True,
                    GL_CULL_FACE: True,
                    'glBlendFunc': (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA),
                },
            )
            paths_items.append(item)
            self.addItem(item)
        return paths_items

    def redraw_paths(self):
        for item in self.paths_items:
            self.removeItem(item)
        self.paths_items = self.draw_points()


class xyzwWidget(BaseView[xyzwScannerVisualizer]):
    def construct_widget(self) -> QWidgetType:
        widget = QTabWidget()
        view = Widget(model=self.model)
        widget.addTab(view, "Scanner")
        return widget


class xyzwSettings(BaseView[xyzwScannerVisualizer]):
    def __init__(self, *args, **kwargs):
        super(xyzwSettings, self).__init__(*args, **kwargs)
        self.settings_table = SettingsTableWidget(
            settings=self.model.get_default_settings(),
            apply=self.apply
        )

    def construct_widget(self) -> QWidgetType:
        widget = QWidget()
        widget.setLayout(QVBoxLayout())
        splitter = QSplitter(orientation=Qt.Orientation.Vertical)
        widget.layout().addWidget(splitter)
        widget.layout().setContentsMargins(0, 0, 0, 0)

        splitter.addWidget(self.settings_table)
        splitter.addWidget(QWidget())
        splitter.setChildrenCollapsible(False)
        splitter.setProperty('type', 'inner')
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
        return widget

    def apply(self):
        self.model.set_settings(self.settings_table.table.to_dict())
