import pyqtgraph.opengl as gl
import pyqtgraph as pg
import numpy as np
from stl import mesh
from PyQt6.QtWidgets import *


def coords_to_GL_coords(func):
    def wrapper(*args, x, y, z):
        return func(*args, x=z, y=x, z=y)
    return wrapper


class ScannerVisualizer(gl.GLViewWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #  here and after X -- GL coord, x -- 'real' coord
        self.room_sizeX = 5  # m
        self.room_sizeY = 3  # m
        self.room_sizeZ = 3  # m

        self.scanner_sizeX = 0.5314
        self.scanner_sizeY = 2.26292
        self.scanner_sizeZ = 2.13709

        self.scanner_offsetX = 0.2
        self.scanner_offsetY = (self.room_sizeY - self.scanner_sizeY) / 2
        self.scanner_offsetZ = 0.3

        points, faces = self.loadSTL('cylinder.stl')
        meshdata = gl.MeshData(vertexes=points, faces=faces)
        self.object_pillar = gl.GLMeshItem(
            meshdata=meshdata,
            smooth=True,
            drawFaces=True,
            color=pg.mkColor((100, 100, 100, 100)),
            glOptions='translucent',  # translucent, opaque, additive
        )

        self.setBackgroundColor(pg.mkColor('white'))

        self.opts['distance'] = 2*max([self.room_sizeX, self.room_sizeY, self.room_sizeZ])
        self.pan(self.room_sizeX / 2, self.room_sizeY / 2, 0)

        self.scanner_pos = {
            'X': 0.5,
            'Y': 0.5,
            'Z': 1,
        }
        self.object_pos = {
            'X': 1,
            'Y': 1,
            'Z': 1,
        }

        self.grid_items = self.draw_grid()
        self.scanner_zone_items = self.draw_scanner_zone()
        self.scanner_items = self.draw_scanner()
        self.object_items = self.draw_object()
        self.draw_text()

    @coords_to_GL_coords
    def set_room_size(self, x: float, y: float, z: float):
        self.room_sizeX, self.room_sizeY, self.room_sizeZ = x, y, z
        self.redraw_grid()

    @coords_to_GL_coords
    def set_scanner_pos(self, x: float, y: float, z: float):
        self.scanner_pos = {'X': x, 'Y': y, 'Z': z}
        self.redraw_scanner()

    @coords_to_GL_coords
    def set_object_pos(self, x: float, y: float, z: float):
        self.object_pos = {'X': x, 'Y': y, 'Z': z}
        self.redraw_object()

    def draw_grid(self):
        """
        Creates grid

        :return:
        """
        gx = gl.GLGridItem()
        gx.setColor('gray')
        gx.setSize(self.room_sizeZ, self.room_sizeY)
        gx.setSpacing(1, 1)
        gx.rotate(90, 0, -1, 0)
        gx.translate(0, self.room_sizeY / 2, self.room_sizeZ / 2)
        self.addItem(gx)

        gy = gl.GLGridItem()
        gy.setColor('gray')
        gy.setSize(self.room_sizeX, self.room_sizeZ)
        gy.setSpacing(1, 1)
        gy.rotate(90, 1, 0, 0)
        gy.translate(self.room_sizeX / 2, 0, self.room_sizeZ / 2)
        self.addItem(gy)

        gz = gl.GLGridItem()
        gz.setColor('gray')
        gz.setSize(self.room_sizeX, self.room_sizeY)
        gz.setSpacing(1, 1)
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
            [0, self.scanner_offsetY, self.scanner_offsetZ],
            [0, self.scanner_offsetY, self.scanner_offsetZ + self.scanner_sizeZ],
            [0, self.scanner_offsetY + self.scanner_sizeY, self.scanner_offsetZ + self.scanner_sizeZ],
            [0, self.scanner_offsetY + self.scanner_sizeY, self.scanner_offsetZ],
            [0, self.scanner_offsetY, self.scanner_offsetZ]
        ]

        zonex = gl.GLLinePlotItem(pos=pts, antialias=True, width=2, color=color1)
        self.addItem(zonex)

        pts = [
            [self.scanner_offsetX, self.scanner_offsetY, 0],
            [self.scanner_offsetX + self.scanner_sizeX, self.scanner_offsetY, 0],
            [self.scanner_offsetX + self.scanner_sizeX, self.scanner_offsetY + self.scanner_sizeY, 0],
            [self.scanner_offsetX, self.scanner_offsetY + self.scanner_sizeY, 0],
            [self.scanner_offsetX, self.scanner_offsetY, 0]
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
        pts = [
            [0, self.scanner_offsetY + self.scanner_pos['Y'], self.scanner_offsetZ + self.scanner_pos['Z']],
            [self.scanner_offsetX + self.scanner_pos['X'], self.scanner_offsetY + self.scanner_pos['Y'],
             self.scanner_offsetZ + self.scanner_pos['Z']]
        ]
        linex = gl.GLLinePlotItem(pos=pts, antialias=True, width=3, color=color1)
        self.addItem(linex)

        pts = [
            [0, 0, self.scanner_offsetZ + self.scanner_pos['Z']],
            [0, self.scanner_offsetY + self.scanner_pos['Y'], self.scanner_offsetZ + self.scanner_pos['Z']]
        ]
        liney = gl.GLLinePlotItem(pos=pts, antialias=True, width=2, color=color1)
        self.addItem(liney)

        pts = [
            [0, self.scanner_offsetY + self.scanner_pos['Y'], 0],
            [0, self.scanner_offsetY + self.scanner_pos['Y'], self.scanner_offsetZ + self.scanner_pos['Z']]
        ]
        linez = gl.GLLinePlotItem(pos=pts, antialias=True, width=2, color=color1)
        self.addItem(linez)

        return linex, liney, linez

    def redraw_scanner(self):
        for item in self.scanner_items:
            self.removeItem(item)
        self.scanner_items = self.draw_scanner()

    def draw_object(self):
        tt = np.eye(4)
        tt[3, 3] = 1
        tt[2, 2] = 10 * self.object_pos['Z']
        tt[0, 0] = 0.2
        tt[1, 1] = 0.2
        tr = pg.Transform3D(tt)
        self.object_pillar.applyTransform(tr, False)
        self.object_pillar.translate(self.object_pos['X'], self.object_pos['Y'], 0)
        self.addItem(self.object_pillar)

        return [self.object_pillar]

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
    def loadSTL(filename):
        m = mesh.Mesh.from_file(filename)
        points = m.points.reshape(-1, 3)
        faces = np.arange(points.shape[0]).reshape(-1, 3)
        return points, faces