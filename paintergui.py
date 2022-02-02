# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'painter.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
import numpy as np
import math
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from mpl_toolkits.mplot3d import Axes3D

from matplotlib.figure import Figure
# from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from MainWindow import Ui_MainWindow


MODES = [

    'line', 'polyline',
    'rect',
]


CANVAS_DIMENSIONS = 600, 600

SELECTION_PEN = QPen(QColor(0xff, 0xff, 0xff), 1, Qt.DashLine)
PREVIEW_PEN = QPen(QColor(0xff, 0xff, 0xff), 1, Qt.SolidLine)





class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):


        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.grid()
        self.ax.mouse_init()


        # self.ax.set_xticks(np.arange(-60,60,1))
        uss = np.linspace(0, 2 * np.pi, 32)
        zss = np.linspace(-100, 100, 2)

        uss, zss = np.meshgrid(uss, zss)

        xss = 250 * np.cos(uss)
        yss = 250 * np.sin(uss)
        self.ax.plot_surface(xss,yss,zss,alpha = 0.5, color = 'grey')
        super(MplCanvas, self).__init__(self.fig)



class Canvas(QLabel):

    mode = 'rect'

    primary_color = QColor(Qt.black)
    # Store configuration settings, including pen width, fonts etc.
    config = {
        # Drawing options.
        'size': 1,
        'fill': True,

    }
    active_color = '#000000'
    preview_pen = None
    timer_event = None
    move = pyqtSignal()

    def initialize(self):
        self.background_color =  QColor(Qt.gray)
        self.eraser_color = QColor(Qt.white)
        self.eraser_color.setAlpha(100)
        self.reset()
        self.xpos =  []
        self.ypos = []
        self.nx = 10
        self.ny = 10
        self.z1 = 1
        self.z2 = 1
        self.poslist = []
        self.cx = 0
        self.cy = 0
        p = QPainter(self.pixmap())
        p.setPen(QPen(QColor(Qt.black), self.config['size'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))


        p.setBrush(QBrush(QColor(Qt.white)))

        p.drawEllipse(QPointF(300,300),250,250)
        p.drawRect(QRectF(550,290,10,20))
        p.drawLine(290,50,560,310)
        p.drawLine(290,550,560,290)
        p.setBrush(QBrush(QColor(Qt.red)))

        p.drawEllipse(QPointF(300,300),1,1)

        # p.drawRect(QRectF(50,290,-10,20))
        # p.drawLine(290,50,40,310)
        # p.drawLine(290,550,40,290)

        self.update()

    def reset(self):
        # Create the pixmap for display.
        self.setPixmap(QPixmap(*CANVAS_DIMENSIONS))

        # Clear the canvas.
        self.pixmap().fill(self.background_color)

        p = QPainter(self.pixmap())
        p.setPen(QPen(QColor(Qt.black), self.config['size'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.setBrush(QBrush(QColor(Qt.white)))
        p.drawEllipse(QPointF(300,300),250,250)
        p.drawRect(QRectF(550,290,10,20))
        p.drawLine(290,50,560,310)
        p.drawLine(290,550,560,290)
        p.setBrush(QBrush(QColor(Qt.red)))

        p.drawEllipse(QPointF(300,300),1,1)

    def set_primary_color(self, hex):
        self.primary_color = QColor(hex)


    def set_mode(self, mode):
        # Clean up active timer animations.
        self.timer_cleanup()
        # Reset mode-specific vars (all)
        self.active_shape_fn = None
        self.active_shape_args = ()

        self.origin_pos = None

        self.current_pos = None
        self.last_pos = None

        self.history_pos = None
        self.last_history = []

        # Apply the mode
        self.mode = mode

    def reset_mode(self):
        self.set_mode(self.mode)

    def on_timer(self):
        if self.timer_event:
            self.timer_event()

    def timer_cleanup(self):
        if self.timer_event:
            # Stop the timer, then trigger cleanup.
            timer_event = self.timer_event
            self.timer_event = None
            timer_event(final=True)

    # Mouse events.

    def mousePressEvent(self, e):
        fn = getattr(self, "%s_mousePressEvent" % self.mode, None)

        dist = ((e.x() - 300)**2 + (e.y()-300)**2)**0.5
        if dist > 250:

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText('Designated point is outside the Machine!')
            msg.setWindowTitle("Error")
            msg.exec_()

        elif  (e.y()  - 310 -  e.x() +  560 < 0):

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText('Designated point is outside of reach!!')
            msg.setWindowTitle("Error")
            msg.exec_()

        elif  (e.y() -290  + e.x() -  560 > 0):

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText('Designated point is outside of reach!')
            msg.setWindowTitle("Error")
            msg.exec_()

        elif e.x() is not None and e.y() is not None:
                self.xpos = np.append(self.xpos,e.x()-300)
                self.ypos = np.append(self.ypos,-e.y()+300)
                if fn:
                    return fn(e)

    def mouseMoveEvent(self, e):
        self.cx = e.x()
        self.cy = e.y()
        self.move.emit()
        fn = getattr(self, "%s_mouseMoveEvent" % self.mode, None)
        if fn:
            return fn(e)

    def mouseReleaseEvent(self, e):
        fn = getattr(self, "%s_mouseReleaseEvent" % self.mode, None)

        dist = ((e.x() - 300)**2 + (e.y()-300)**2)**0.5
        if dist > 250:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText('Designated point is outside the Machine!')
            msg.setWindowTitle("Error")
            msg.exec_()
        elif  (e.y()  - 310 -  e.x() +  560 < 0):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText('Designated point is outside of reach!!')
            msg.setWindowTitle("Error")
            msg.exec_()
        elif  (e.y() -290  + e.x() -  560 > 0):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText('Designated point is outside of reach!')
            msg.setWindowTitle("Error")
            msg.exec_()

        elif e.x() is not None and e.y() is not None:
                self.xpos = np.append(self.xpos,e.x()-300)
                self.ypos = np.append(self.ypos,-e.y()+300)
                if fn:
                    return fn(e)

    def mouseDoubleClickEvent(self, e):
        fn = getattr(self, "%s_mouseDoubleClickEvent" % self.mode, None)
        if fn:
            return fn(e)


        self.last_pos = None

    # Mode-specific events.


    def generic_shape_mousePressEvent(self, e):
        self.origin_pos = e.pos()
        self.current_pos = e.pos()
        self.timer_event = self.generic_shape_timerEvent

    def generic_shape_timerEvent(self, final=False):
        p = QPainter(self.pixmap())
        p.setCompositionMode(QPainter.RasterOp_SourceXorDestination)
        pen = self.preview_pen
        p.setPen(pen)
        if self.last_pos:
            getattr(p, self.active_shape_fn)(QRect(self.origin_pos, self.last_pos), *self.active_shape_args)

        if not final:
            p.setPen(pen)
            getattr(p, self.active_shape_fn)(QRect(self.origin_pos, self.current_pos), *self.active_shape_args)

        self.update()
        self.last_pos = self.current_pos

    def generic_shape_mouseMoveEvent(self, e):
        self.current_pos = e.pos()

    def generic_shape_mouseReleaseEvent(self, e):
        if self.last_pos:
            # Clear up indicator.
            self.timer_cleanup()

            p = QPainter(self.pixmap())
            p.setPen(QPen(self.primary_color, self.config['size'], Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin))

            if self.config['fill']:
                p.setBrush(QBrush(self.primary_color))
            getattr(p, self.active_shape_fn)(QRect(self.origin_pos, e.pos()), *self.active_shape_args)
            self.update()

        self.reset_mode()

    # Line events

    def line_mousePressEvent(self, e):
        self.origin_pos = e.pos()
        self.current_pos = e.pos()
        self.preview_pen = PREVIEW_PEN
        self.timer_event = self.line_timerEvent

    def line_timerEvent(self, final=False):
        p = QPainter(self.pixmap())
        p.setCompositionMode(QPainter.RasterOp_SourceXorDestination)
        pen = self.preview_pen
        p.setPen(pen)
        if self.last_pos:
            p.drawLine(self.origin_pos, self.last_pos)

        if not final:
            p.drawLine(self.origin_pos, self.current_pos)

        self.update()
        self.last_pos = self.current_pos

    def line_mouseMoveEvent(self, e):
        self.current_pos = e.pos()

    def line_mouseReleaseEvent(self, e):
        if self.last_pos:
            # Clear up indicator.
            self.timer_cleanup()

            p = QPainter(self.pixmap())
            p.setPen(QPen(self.primary_color, self.config['size'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

            p.drawLine(self.origin_pos, e.pos())
            self.update()

        self.reset_mode()

    # Generic poly events
    def generic_poly_mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            if self.history_pos:
                self.history_pos.append(e.pos())
            else:
                self.history_pos = [e.pos()]
                self.current_pos = e.pos()
                self.timer_event = self.generic_poly_timerEvent

        elif e.button() == Qt.RightButton and self.history_pos:
            # Clean up, we're not drawing
            self.timer_cleanup()
            self.reset_mode()

    def generic_poly_timerEvent(self, final=False):
        p = QPainter(self.pixmap())
        p.setCompositionMode(QPainter.RasterOp_SourceXorDestination)
        pen = self.preview_pen
        p.setPen(pen)
        if self.last_history:
            getattr(p, self.active_shape_fn)(*self.last_history)

        if not final:
            p.setPen(pen)
            getattr(p, self.active_shape_fn)(*self.history_pos + [self.current_pos])

        self.update()
        self.last_pos = self.current_pos
        self.last_history = self.history_pos + [self.current_pos]

    def generic_poly_mouseMoveEvent(self, e):
        self.current_pos = e.pos()

    def generic_poly_mouseDoubleClickEvent(self, e):
        self.timer_cleanup()
        p = QPainter(self.pixmap())
        p.setPen(QPen(self.primary_color, self.config['size'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))


        getattr(p, self.active_shape_fn)(*self.history_pos + [e.pos()])
        self.update()
        self.reset_mode()

    # Polyline events

    def polyline_mousePressEvent(self, e):
        self.active_shape_fn = 'drawPolyline'
        self.preview_pen = PREVIEW_PEN
        self.generic_poly_mousePressEvent(e)

    def polyline_timerEvent(self, final=False):
        self.generic_poly_timerEvent(final)

    def polyline_mouseMoveEvent(self, e):
        self.generic_poly_mouseMoveEvent(e)

    def polyline_mouseDoubleClickEvent(self, e):
        self.generic_poly_mouseDoubleClickEvent(e)

    # Rectangle events

    def rect_mousePressEvent(self, e):
        self.active_shape_fn = 'drawRect'
        self.active_shape_args = ()
        self.preview_pen = PREVIEW_PEN
        self.generic_shape_mousePressEvent(e)

    def rect_timerEvent(self, final=False):
        self.generic_shape_timerEvent(final)

    def rect_mouseMoveEvent(self, e):
        self.generic_shape_mouseMoveEvent(e)

    def rect_mouseReleaseEvent(self, e):
        self.generic_shape_mouseReleaseEvent(e)





    def resetpos(self,arg):
        self.xpos = []
        self.ypos = []
        arg.saveButton.setEnabled(False)

#####everything internal is handled in coordinate units.
###########means output list is also in coord units.
########## 1 cm = 5pixel.

    def set_status(self,arg):
        self.nx = 5*float(arg.xres.text())
        self.ny = 5*float(arg.yres.text())
        self.nz = 5*float(arg.zres.text())
        self.z1 = float(arg.z1.text())
        self.z2 = float(arg.z2.text())

    def print_positions(self):
        # print(self.xpos)
        # print(self.ypos)
        # self.set_status()
        mode = self.mode
        if mode == "line":
            self.get_positionsline()
            # self.update_graph(self.poslist)

        elif mode == "rect":
            self.get_positionsrect()
            # self.update_graph(self.poslist)

        elif mode == "polyline":
            self.get_positionspoly()
            # self.update_graph(self.poslist)




    def get_positionsrect(self):
        poslist = []
        for i in range(0,len(self.xpos)-1,2):
            xmax = self.xpos[i+1]
            xmin = self.xpos[i]
            ymax = self.ypos[i+1]
            ymin = self.ypos[i]
            nx = self.nx
            ny = self.ny
            nz = self.nz

            linvalz = abs(math.floor((self.z2-self.z1)/(nz)))

            linvalx = abs(math.floor((xmax-xmin)/(nx)))
            linvaly = abs(math.floor((ymax-ymin)/(ny)))

            zvals = np.linspace(self.z1,self.z2,linvalz+1)
            xpos = np.linspace(xmin,xmax,linvalx+1)
            ypos = np.linspace(ymin,ymax,linvaly+1)

            #I didn't understand the earlier get_positions code so I've rewritten it.
            positions = []
            for z in range(0,len(zvals)):
                for x in range(0,len(xpos)):
                    for y in range(0,len(ypos)):
                        positions.append(  [ xpos[x],ypos[y],zvals[z] ]  )


            poslist.extend(positions)
            # print(poslist)
            self.poslist = poslist



    def get_positionsline(self):
            poslist = []
            xs = self.xpos
            ys = self.ypos

            nz = self.nz

            linvalz = abs(math.floor((self.z2-self.z1)/(nz)))
            zvals = np.linspace(self.z1,self.z2,linvalz+1)
            xpos = [xs[0]]
            ypos = [ys[0]]
#            zpos = [zs[0]]

            for i in range(0,len(xs)-1,2):

        #general idea for motion list- user gave end points of line segments.
        #each point is essentially a location in the array. Get distance between the
        #two array points.    #Get an equation of the line joining two points in the array.
            #Get real coordinates of the point on this line at every
        #  'res' distance.




        #the coordinates of the two end points of line segment

                xposi = xs[i]
                xposi2 = xs[i+1]

                yposi = ys[i]
                yposi2 = ys[i+1]

                # zposi = zs[i]
                # zposi2 =zs[i+1]
                res= (self.nx**2 + self.ny**2)**0.5
                length = ((xposi2-xposi)**2 + (yposi2-yposi)**2)**0.5
                linval = math.floor(length/(res))

                parvals = np.linspace(0,1,linval+1)

                for t in parvals[1:]: #first start point already initialized in array.
            ##Other start points are incorporated as the end points of previous segment.

                    xval = xposi + t*(xposi2 - xposi)
                    yval = yposi + t*(yposi2 - yposi)
                    # zval = zposi + t*(zposi2 - zposi)
                    xpos = np.append(xpos,xval)
                    ypos = np.append(ypos,yval)


            for z in range(0,len(zvals)):
                zpos = z*np.ones(len(xpos))
                positions = list(zip(xpos,ypos,zpos))
                poslist = poslist + positions




            self.poslist = poslist

    def get_positionspoly(self):
        poslist = []
        xs = np.delete(self.xpos,-1)
        ys = np.delete(self.ypos,-1)

        xs = xs[1::2]
        ys = ys[1::2]
        xpos = [xs[0]]
        ypos = [ys[0]]

        for i in range(0,len(xs)-1):
                    xposi = xs[i]
                    xposi2 = xs[i+1]

                    yposi = ys[i]
                    yposi2 = ys[i+1]

                    res= (self.nx**2 + self.ny**2)**0.5
                    length = ((xposi2-xposi)**2 + (yposi2-yposi)**2)**0.5
                    linval = math.floor(length/(res))

                    parvals = np.linspace(0,1,linval+1)

                    for t in parvals[1:]: #first start point already initialized in array.
                    ##Other start points are incorporated as the end points of previous segment.

                        xval = xposi + t*(xposi2 - xposi)
                        yval = yposi + t*(yposi2 - yposi)
                        # zval = zposi + t*(zposi2 - zposi)
                        xpos = np.append(xpos,xval)
                        ypos = np.append(ypos,yval)

        nz = self.nz

        linvalz = abs(math.floor((self.z2-self.z1)/(nz)))
        zvals = np.linspace(self.z1,self.z2,linvalz+1)

        for z in range(0,len(zvals)):
            zpos = z*np.ones(len(xpos))
            positions = list(zip(xpos,ypos,zpos))
            poslist = poslist+ positions




        self.poslist = poslist

    def checklist(self,arg):
        # self.set_status()
        xs = [x[0]+300 for x in self.poslist]
        ys = [-x[1]+300 for x in self.poslist]

        for i in range(0,len(xs)):
            dist = ((xs[i] - 300)**2 + (ys[i]-300)**2)**0.5
            if (dist > 250):
                arg.saveButton.setEnabled(False)

                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Error")
                msg.setInformativeText('Some designated points are outside of the machine!')
                msg.setWindowTitle("Error")
                msg.exec_()
                break

            elif  (ys[i]  - 310 -  xs[i] +  560 < 0):
                arg.saveButton.setEnabled(False)
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Error")
                msg.setInformativeText('Some designated points are outside of reach!!')
                msg.setWindowTitle("Error")
                msg.exec_()
                break
            elif  (ys[i] -290  + xs[i] - 560 > 0):
                arg.saveButton.setEnabled(False)
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Error")
                msg.setInformativeText('Some designated points are outside of reach!')
                msg.setWindowTitle("Error")
                msg.exec_()
                break
            else:
                arg.saveButton.setEnabled(True)

    def coordEnter(self,arg):

        if self.mode == 'polyline':
            res = min(self.nx , self.ny , self.nz)
            str1 = arg.ps.text()
            #split the string by , in order to get an array
            str1 = np.array(str1.replace('(','').replace(')','').split(','),dtype=float).reshape(-1,3)
            try:

                xs = [5*x[0] for x in str1]
                ys = [5*x[1] for x in str1]
                zs = [5*x[2] for x in str1]
                xpos = [xs[0]]
                ypos = [ys[0]]
                zpos = [zs[0]]
                p = QPainter(self.pixmap())
                p.setPen(QPen(QColor(Qt.black), self.config['size'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                p.setBrush(QBrush(QColor(Qt.black)))

                for i in range(0,len(xs)-1):
                    p.drawLine(QPointF(xs[i]+300,-ys[i]+300),QPointF(xs[i+1]+300,-ys[i+1]+300))

                for i in range(0,len(xs)-1):

                    xposi = xs[i]
                    xposi2 = xs[i+1]

                    yposi = ys[i]
                    yposi2 = ys[i+1]

                    zposi = zs[i]
                    zposi2 =zs[i+1]

                    length = ((xposi2-xposi)**2 + (yposi2-yposi)**2 + (zposi2-zposi)**2)**0.5
                    linval = math.floor(length/(res))

                    parvals = np.linspace(0,1,linval+1)

                    for t in parvals[1:]:

                        xval = xposi + t*(xposi2 - xposi)
                        yval = yposi + t*(yposi2 - yposi)
                        zval = zposi + t*(zposi2 - zposi)
                        xpos = np.append(xpos,xval)
                        ypos = np.append(ypos,yval)
                        zpos = np.append(zpos,zval)





                positions = list(zip(xpos,ypos,zpos))
                self.poslist = positions

            except ValueError:
                QMessageBox.about(self, "Error", "Position should be valid numbers.")

        elif self.mode == 'line':
            res = min(self.nx , self.ny , self.nz)
            str1 = arg.ps.text()
            #split the string by , in order to get an array
            str1 = np.array(str1.replace('(','').replace(')','').split(','),dtype=float).reshape(-1,3)
            try:

                xs = [5*x[0] for x in str1]
                ys = [5*x[1] for x in str1]
                zs = [5*x[2] for x in str1]
                xpos = [xs[0]]
                ypos = [ys[0]]
                zpos = [zs[0]]

                p = QPainter(self.pixmap())
                p.setPen(QPen(QColor(Qt.black), self.config['size'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                p.setBrush(QBrush(QColor(Qt.black)))

                for i in range(0,len(xs)-1,2):
                    p.drawLine(QPointF(xs[i]+300,-ys[i]+300),QPointF(300+xs[i+1],-ys[i+1]+300))


                for i in range(0,len(xs)-1,2):

                    xposi = xs[i]
                    xposi2 = xs[i+1]

                    yposi = ys[i]
                    yposi2 = ys[i+1]

                    zposi = zs[i]
                    zposi2 =zs[i+1]

                    length = ((xposi2-xposi)**2 + (yposi2-yposi)**2 + (zposi2-zposi)**2)**0.5
                    linval = math.floor(length/(res))

                    parvals = np.linspace(0,1,linval+1)

                    for t in parvals[1:]:

                        xval = xposi + t*(xposi2 - xposi)
                        yval = yposi + t*(yposi2 - yposi)
                        zval = zposi + t*(zposi2 - zposi)
                        xpos = np.append(xpos,xval)
                        ypos = np.append(ypos,yval)
                        zpos = np.append(zpos,zval)


                positions = list(zip(xpos,ypos,zpos))
                self.poslist = positions

            except ValueError:
                QMessageBox.about(self, "Error", "Position should be valid numbers.")

        elif self.mode == 'rect':

            res = min(self.nx , self.ny , self.nz)
            str1 = arg.ps.text()
            #split the string by , in order to get an array
            str1 = np.array(str1.replace('(','').replace(')','').split(','),dtype=float).reshape(-1,3)
            try:

                xs = [5*x[0] for x in str1]
                ys = [5*x[1] for x in str1]
                zs = [5*x[2] for x in str1]
                self.xpos = xs
                self.ypos = ys

                p = QPainter(self.pixmap())
                p.setPen(QPen(QColor(Qt.black), self.config['size'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                p.setBrush(QBrush(QColor(Qt.black)))
                for i in range(0,len(xs)-1,2):
                    p.drawRect(QRectF(xs[i]+300,-ys[i]+300,xs[i+1]-xs[i],-ys[i+1]+ys[i]))

                poslist = []
                for i in range(0,len(self.xpos)-1,2):
                    xmax = self.xpos[i+1]
                    xmin = self.xpos[i]
                    ymax = self.ypos[i+1]
                    ymin = self.ypos[i]
                    zmax = zs[i+1]
                    zmin = zs[i]
                    nx = self.nx
                    ny = self.ny
                    nz = self.nz

                    linvalz = abs(math.floor((zmax-zmin)/(nz)))

                    linvalx = abs(math.floor((xmax-xmin)/(nx)))
                    linvaly = abs(math.floor((ymax-ymin)/(ny)))

                    zvals = np.linspace(zmin,zmax,linvalz+1)
                    xpos = np.linspace(xmin,xmax,linvalx+1)
                    ypos = np.linspace(ymin,ymax,linvaly+1)

                    positions = []
                    for z in range(0,len(zvals)):
                        for x in range(0,len(xpos)):
                            for y in range(0,len(ypos)):
                                positions.append(  [ xpos[x],ypos[y],zvals[z] ]  )


                    poslist.extend(positions)
                    # print(poslist)
                    self.poslist = poslist



            except ValueError:
                QMessageBox.about(self, "Error", "Position should be valid numbers.")




    def save_file(self):

        with open("file.txt", 'w') as file:
            for row in self.poslist:
                s = " ".join(map(str, row))
                file.write(s+'\n')

        with open("res.txt", 'w') as file:
            file.write(str(self.nx/5)+ ' '+ str(self.ny/5)+' '+ str(self.nz/5))

class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # Replace canvas placeholder from QtDesigner.
        # self.horizontalLayout.removeWidget(self.canvas)
        self.canvas = Canvas()
        self.canvas.initialize()
        # We need to enable mouse tracking to follow the mouse without the button pressed.
        self.canvas.setMouseTracking(True)
        # Enable focus to capture key inputs.
        self.canvas.setFocusPolicy(Qt.StrongFocus)
        self.horizontalLayout_3.addWidget(self.canvas)

        self.canvas2 = MplCanvas()
        self.horizontalLayout_3.addWidget(self.canvas2)





        # Setup the mode buttons
        mode_group = QButtonGroup(self)
        mode_group.setExclusive(True)

        for mode in MODES:
            btn = getattr(self, '%sButton' % mode)
            btn.pressed.connect(lambda mode=mode: self.canvas.set_mode(mode))
            mode_group.addButton(btn)

        self.printButton.clicked.connect(lambda: [self.canvas.print_positions(),self.update_graph(self.canvas.poslist,self.canvas.nx,self.canvas.ny)])
        self.clearButton.clicked.connect(lambda: [self.canvas.reset(),self.canvas.resetpos(self)])
        self.saveButton.clicked.connect(lambda: self.canvas.save_file())
        self.verifyButton.clicked.connect(lambda: self.canvas.checklist(self))
        self.EntButton.clicked.connect(lambda: [self.canvas.resetpos(self), self.canvas.coordEnter(self),self.update_graph(self.canvas.poslist,self.canvas.nx,self.canvas.ny)])


        # Initialize animation timer.
        self.timer = QTimer()
        self.timer.timeout.connect(self.canvas.on_timer)
        self.timer.setInterval(100)
        self.timer.start()

        self.xres.editingFinished.connect(lambda: self.canvas.set_status(self))
        self.yres.editingFinished.connect(lambda: self.canvas.set_status(self))
        self.zres.editingFinished.connect(lambda: self.canvas.set_status(self))

        self.z1.editingFinished.connect(lambda: self.canvas.set_status(self))
        self.z2.editingFinished.connect(lambda: self.canvas.set_status(self))
        self.canvas.move.connect(lambda: self.updateCoord(self.canvas.cx,self.canvas.cy))




        sizeicon = QLabel()
        sizeicon.setPixmap(QPixmap(os.path.join('images', 'border-weight.png')))


        self.show()

    def update_graph(self,poslist,nx,ny):


            self.horizontalLayout_3.removeWidget(self.canvas2)

            self.canvas2 = MplCanvas()
            self.canvas2.ax.set_xlim3d(-300,300)
            self.canvas2.ax.set_ylim3d(-300,300)
            self.canvas2.ax.set_zlim3d(-300,300)

            xs = [x[0] for x in poslist]
            ys = [x[1] for x in poslist]
            zs = [x[2] for x in poslist]
            size = 0.5*min([nx,ny])


            self.canvas2.ax.scatter(xs,ys,zs,s = size)

            self.horizontalLayout_3.addWidget(self.canvas2)

    def updateCoord(self,x,y):
        self.label_Coord.setText('Mouse coords: ( %d , %d )' % ((x-300)/5,(-y+300)/5))





#################################################################################








if __name__ == '__main__':

    app = QApplication([])
    window = MainWindow()
    app.exec_()
