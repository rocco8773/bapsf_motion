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
import toml
from matplotlib.figure import Figure
# from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from MainWindow import Ui_MainWindow


MODES = [

    'line', 'polyline',
    'rect', 'barrier', 'circle', 'ellipse'
]


GRIDS = [


    'rect', 'circle', 'ellipse','sphere'
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
        zss = np.linspace(-3, 3, 2)

        uss, zss = np.meshgrid(uss, zss)

        xss = 50 * np.cos(uss)
        yss = 50 * np.sin(uss)
        self.ax.plot_surface(xss, yss, zss, alpha=0.5, color='grey')
        super(MplCanvas, self).__init__(self.fig)


class Canvas(QLabel):
    '''This class controls the "canvas" where one can draw the shapes to define
    data acquisition regions in 2D (3D with z-axis extrusion). '''

    mode = 'rect'
    grid = 'rect'

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
        self.background_color = QColor(Qt.gray)
        self.eraser_color = QColor(Qt.white)
        self.last_pos = None
        self.eraser_color.setAlpha(100)
        self.hand = 0
        self.reset()
        self.xpos = []
        self.ypos = []
        self.nx = 10
        self.ny = 10
        self.nz = 1
        self.z1 = 1
        self.z2 = 1
        self.poslist = []
        self.barlist = []
        self.cx = 0
        self.cy = 0
        self.bar = 0
        self.centers = ''
        self.closeit = False
        
        p = QPainter(self.pixmap())
        p.setPen(QPen(QColor(Qt.black),
                 self.config['size'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

        p.setBrush(QBrush(QColor(Qt.red)))

        p.drawEllipse(QPointF(300, 300), 1, 1)

        p.setBrush(QBrush(QColor(Qt.white)))

        p.drawEllipse(QPointF(300, 300), 250, 250)
        if self.hand == 0:
            p.drawRect(QRectF(550, 290, 10, 20))
            p.drawLine(290, 50, 560, 310)
            p.drawLine(290, 550, 560, 290)

        elif self.hand == 1:
            p.drawRect(QRectF(50, 290, -10, 20))
            p.drawLine(290, 50, 40, 310)
            p.drawLine(290, 550, 40, 290)

        self.update()

    def reset(self):
        ''' Reset the canvas, and associated data'''
        # Create the pixmap for display.
        self.setPixmap(QPixmap(*CANVAS_DIMENSIONS))

        # Clear the canvas.
        self.pixmap().fill(self.background_color)

        p = QPainter(self.pixmap())
        p.setPen(QPen(QColor(Qt.black),
                 self.config['size'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.setBrush(QBrush(QColor(Qt.white)))
        p.drawEllipse(QPointF(300, 300), 250, 250)

        if self.hand == 0:
            p.drawRect(QRectF(550, 290, 10, 20))
            p.drawLine(290, 50, 560, 310)
            p.drawLine(290, 550, 560, 290)
        elif self.hand == 1:
            p.drawRect(QRectF(50, 290, -10, 20))
            p.drawLine(290, 50, 40, 310)
            p.drawLine(290, 550, 40, 290)

        p.setBrush(QBrush(QColor(Qt.red)))

        p.drawEllipse(QPointF(300, 300), 1, 1)

    def set_primary_color(self, hex):
        self.primary_color = QColor(hex)

    def set_hand(self):
        ''' Sets ''chirality'' i.e. Left or Right entry point.'''
        if self.hand == 0:
            self.hand = 1
        elif self.hand == 1:
            self.hand = 0

        self.reset()

    def set_mode(self, mode ):
        ''' This mode controls the shape painting function, 
        as well as the point generator'''
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
        #Apply Mode
        self.mode = mode

    def set_grid(self, grid):
        ''' similar to mode system, sets the grid system'''
        self.grid = grid

            
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
    ''' redefining pyqt mouse events... depending on chosen mode, 
    this will also call  a mode specific  drawing function to paint shape 
    on the canvas'''
    
    """Everything internal is handled in coordinate units. 
    ###### EXCEPT THE BARLIST
    # All inputs are taken in cm units.
    # means output list is also in coord units.
    # 1 cm = 5pixel, as per the set size of the canvas.
    # self.xpos, self.ypos (and self.zpos) are containers for all vertex points.
    Basic point verification routine- distance from centre (is_inside_machine?)
    
    Angle from entry point (can probe reach via ball-valve. )### CURRENTLY COMPLETELY AD-HOC ##### 
    Current angle-restriction setup-
    \_ Hole perfectly aligned with centre of lapd, + exacty at the edge of lapd.
    valve is 2 cm long, and 2 cm above and below hole. SO shaft makes 45 degree angles at max.. definitely incorrect.
    """
    
    
    def mousePressEvent(self, e):
        fn = getattr(self, "%s_mousePressEvent" % self.mode, None)
### calls mode_specific canvas drawing function- 

### Basic Point validity verification routine:
        dist = ((e.x() - 300)**2 + (e.y()-300)**2)**0.5
        if dist > 250:

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText('Designated point is outside the Machine!')
            msg.setWindowTitle("Error")
            msg.exec_()

        if self.hand == 0:

            if (e.y() - 310 - e.x() + 560 < 0):

                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Error")
                msg.setInformativeText(
                    'Designated point is outside of reach!!')
                msg.setWindowTitle("Error")
                msg.exec_()

            elif (e.y() - 290 + e.x() - 560 > 0):

                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Error")
                msg.setInformativeText('Designated point is outside of reach!')
                msg.setWindowTitle("Error")
                msg.exec_()

        if self.hand == 1:
            if (e.y() - 310 + e.x() - 40 < 0):

                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Error")
                msg.setInformativeText(
                    'Designated point is outside of reach!!')
                msg.setWindowTitle("Error")
                msg.exec_()

            elif (e.y() - 290 - e.x() + 40 > 0):

                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Error")
                msg.setInformativeText('Designated point is outside of reach!')
                msg.setWindowTitle("Error")
                msg.exec_()

        if e.x() is not None and e.y() is not None:
           
            self.xpos = np.append(self.xpos, e.x()-300)
            self.ypos = np.append(self.ypos, -e.y()+300)
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
### calls mode_specific function- 

### Basic Point validity verification routine:
        dist = ((e.x() - 300)**2 + (e.y()-300)**2)**0.5
        if dist > 250:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText('Designated point is outside the Machine!')
            msg.setWindowTitle("Error")
            msg.exec_()
        if self.hand == 0:
            if (e.y() - 310 - e.x() + 560 < 0):

                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Error")
                msg.setInformativeText(
                    'Designated point is outside of reach!!')
                msg.setWindowTitle("Error")
                msg.exec_()

            elif (e.y() - 290 + e.x() - 560 > 0):

                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Error")
                msg.setInformativeText('Designated point is outside of reach!')
                msg.setWindowTitle("Error")
                msg.exec_()

        if self.hand == 1:
            if (e.y() - 310 + e.x() - 40 < 0):

                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Error")
                msg.setInformativeText(
                    'Designated point is outside of reach!!')
                msg.setWindowTitle("Error")
                msg.exec_()

            elif (e.y() - 290 - e.x() + 40 > 0):

                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Error")
                msg.setInformativeText('Designated point is outside of reach!')
                msg.setWindowTitle("Error")
                msg.exec_()

        if e.x() is not None and e.y() is not None:
            self.xpos = np.append(self.xpos, e.x()-300)
            self.ypos = np.append(self.ypos, -e.y()+300)
            if fn:
                return fn(e)

    def mouseDoubleClickEvent(self, e):
        fn = getattr(self, "%s_mouseDoubleClickEvent" % self.mode, None)
        if fn:
            return fn(e)

        self.last_pos = None

    # Mode-specific events.
   
    

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
            p.setPen(QPen(self.primary_color,
                     self.config['size'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

            p.drawLine(self.origin_pos, e.pos())
            self.update()

        self.reset_mode()

    # barrier events

    def barrier_mousePressEvent(self, e):
        self.origin_pos = e.pos()
        self.current_pos = e.pos()
        self.preview_pen = PREVIEW_PEN
        self.timer_event = self.barrier_timerEvent

    def barrier_timerEvent(self, final=False):
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

    def barrier_mouseMoveEvent(self, e):
        self.current_pos = e.pos()

    def barrier_mouseReleaseEvent(self, e):
        if self.last_pos:
            # Clear up indicator.
            self.timer_cleanup()

            p = QPainter(self.pixmap())
            p.setPen(QPen(QColor('#800000'),
                     self.config['size'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

            p.drawLine(self.origin_pos, e.pos())

            p.setPen(QPen(QColor('#FF0000'),
                     self.config['size'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

            if self.hand == 1:
                C = (-self.origin_pos.y() + 300)/(self.origin_pos.x() - 50)
                xv = (100*C*C + 600 + np.sqrt((100*C*C + 600)**2 - 4 *
                      (C*C+1)*(2500*C*C + 90000-250**2)))/(2*(C*C+1))
                yv = -300 + C*(xv-50)
                p.drawLine(self.origin_pos, QPointF(xv, -yv))

                C = (-e.y() + 300)/(e.x() - 50)
                xv = (100*C*C + 600 + np.sqrt((100*C*C + 600)**2 - 4 *
                      (C*C+1)*(2500*C*C + 90000-250**2)))/(2*(C*C+1))
                yv = -300 + C*(xv-50)
                p.drawLine(e.pos(), QPointF(xv, -yv))

            if self.hand == 0:
                C = (-self.origin_pos.y() + 300)/(self.origin_pos.x() - 550)
                xv = (1100*C*C + 600 - np.sqrt((1100*C*C + 600)**2 - 4 *
                      (C*C+1)*(550*550*C*C + 90000-250**2)))/(2*(C*C+1))
                yv = -300 + C*(xv-550)
                p.drawLine(self.origin_pos, QPointF(xv, -yv))

                C = (-e.y() + 300)/(e.x() - 550)
                xv = (1100*C*C + 600 - np.sqrt((1100*C*C + 600)**2 - 4 *
                      (C*C+1)*(550*550*C*C + 90000-250**2)))/(2*(C*C+1))
                yv = -300 + C*(xv-550)
                p.drawLine(e.pos(), QPointF(xv, -yv))

            self.update()
            self.bar += 2
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
            getattr(p, self.active_shape_fn)(
                *self.history_pos + [self.current_pos])

        self.update()
        self.last_pos = self.current_pos
        self.last_history = self.history_pos + [self.current_pos]

    def generic_poly_mouseMoveEvent(self, e):
        self.current_pos = e.pos()

    def generic_poly_mouseDoubleClickEvent(self, e):
        self.timer_cleanup()
        p = QPainter(self.pixmap())
        p.setPen(QPen(self.primary_color,
                 self.config['size'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

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
        self.origin_pos = e.pos()
        self.current_pos = e.pos()
        self.timer_event = self.rect_timerEvent

    def rect_timerEvent(self, final=False):
        p = QPainter(self.pixmap())
        p.setCompositionMode(QPainter.RasterOp_SourceXorDestination)
        pen = self.preview_pen
        p.setPen(pen)
        if self.last_pos:
            getattr(p, self.active_shape_fn)(
                QRect(self.origin_pos, self.last_pos), *self.active_shape_args)

        if not final:
            p.setPen(pen)
            getattr(p, self.active_shape_fn)(
                QRect(self.origin_pos, self.current_pos), *self.active_shape_args)

        self.update()
        self.last_pos = self.current_pos

    def rect_mouseMoveEvent(self, e):
        self.current_pos = e.pos()

    def rect_mouseReleaseEvent(self, e):
        if self.last_pos:
            # Clear up indicator.
            self.timer_cleanup()

            p = QPainter(self.pixmap())
            p.setPen(QPen(self.primary_color,
                     self.config['size'], Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin))

            if self.config['fill']:
                p.setBrush(QBrush(self.primary_color))
            getattr(p, self.active_shape_fn)(
                QRect(self.origin_pos, e.pos()), *self.active_shape_args)
            self.update()

        self.reset_mode()

    # Circle events

    def circle_mousePressEvent(self, e):
        self.active_shape_fn = 'drawEllipse'
        self.active_shape_args = ()
        self.preview_pen = PREVIEW_PEN
        self.origin_pos = e.pos()
        self.current_pos = e.pos()
        self.timer_event = self.circle_timerEvent

    def circle_timerEvent(self, final=False):
        p = QPainter(self.pixmap())
        p.setCompositionMode(QPainter.RasterOp_SourceXorDestination)
        pen = self.preview_pen
        p.setPen(pen)
        if self.last_pos:
            r = np.sqrt((self.origin_pos.x() - self.last_pos.x()) **
                        2 + (self.origin_pos.y() - self.last_pos.y())**2)

            getattr(p, self.active_shape_fn)(
                self.origin_pos, r, r, *self.active_shape_args)

        if not final:
            p.setPen(pen)
            r = np.sqrt((self.origin_pos.x() - self.current_pos.x())
                        ** 2 + (self.origin_pos.y() - self.current_pos.y())**2)
            getattr(p, self.active_shape_fn)(
                self.origin_pos, r, r, *self.active_shape_args)

        self.update()
        self.last_pos = self.current_pos

    def circle_mouseMoveEvent(self, e):
        self.current_pos = e.pos()

    def circle_mouseReleaseEvent(self, e):
        if self.last_pos:
            # Clear up indicator.
            self.timer_cleanup()
            r = np.sqrt((self.origin_pos.x() - self.last_pos.x()) **
                        2 + (self.origin_pos.y() - self.last_pos.y())**2)

            p = QPainter(self.pixmap())
            p.setPen(QPen(self.primary_color,
                     self.config['size'], Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin))

            if self.config['fill']:
                p.setBrush(QBrush(self.primary_color))
            getattr(p, self.active_shape_fn)(
                self.origin_pos, r, r, *self.active_shape_args)
            self.update()

        self.reset_mode()

# Ellipse events
    def ellipse_mousePressEvent(self, e):
        self.active_shape_fn = 'drawEllipse'
        self.active_shape_args = ()
        self.origin_pos = e.pos()
        self.preview_pen = PREVIEW_PEN
        self.current_pos = e.pos()
        self.timer_event = self.ellipse_timerEvent

    def ellipse_timerEvent(self, final=False):
        p = QPainter(self.pixmap())
        p.setCompositionMode(QPainter.RasterOp_SourceXorDestination)
        pen = self.preview_pen
        p.setPen(pen)
        if self.last_pos:
            getattr(p, self.active_shape_fn)(
                QRect(self.origin_pos, self.last_pos), *self.active_shape_args)

        if not final:
            p.setPen(pen)
            getattr(p, self.active_shape_fn)(
                QRect(self.origin_pos, self.current_pos), *self.active_shape_args)

        self.update()
        self.last_pos = self.current_pos

    def ellipse_mouseMoveEvent(self, e):
        self.current_pos = e.pos()

    def ellipse_mouseReleaseEvent(self, e):
        if self.last_pos:
            # Clear up indicator.
            self.timer_cleanup()

            p = QPainter(self.pixmap())
            p.setPen(QPen(self.primary_color,
                     self.config['size'], Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin))

            if self.config['fill']:
                p.setBrush(QBrush(self.primary_color))
            getattr(p, self.active_shape_fn)(
                QRect(self.origin_pos, e.pos()), *self.active_shape_args)
            self.update()

        self.reset_mode()

    def resetpos(self, arg):
        self.xpos = []
        self.ypos = []
        self.poslist = []
        self.barlist = []
        self.bar = 0
        arg.saveButton.setEnabled(False)



    def set_status(self, arg):
        """ Register resolution and z-axis extrusion inputs. 
        5x factor for cm to pixel conversion"""
        self.nx = 5*float(arg.xres.text())
        self.ny = 5*float(arg.yres.text())
        self.nz = 5*float(arg.zres.text())
        self.z1 = 5*float(arg.z1.text())
        self.z2 = 5*float(arg.z2.text())
        self.centers = str(arg.gridCentre.text())
        self.closeit = arg.closeit
        self.eccentricity = arg.eccentricity

    def set_numpoint(self,arg):
        '''
        sets input (no. of points) for shape autogeneration scheme.
        '''
        self.ea = str(arg.ea.text())
        self.eb = str(arg.eb.text())
        
    def print_positions(self, arg):
        """ Position generating function, for display purposes.
        First- Generates the barrier from given points, as well as the 
         region that becomes no-go zone.  Currently based off ad-hoc 
         assumptions for the angular reach of a probe shaft from a particular 
         valve.
        Second- Calls point generating function depending on the mode.
        Each point generating function further looks at grid config to setup points.
        """
      
        mode = self.mode
        bar = self.bar
        self.zpos = [self.z1, self.z2] #Z-extrusion range
        barlist = []
        arg.saveButton.setEnabled(False)  #Must verify to reenable button
        
        ### Generate the barrier from given points, as well as the 
        ### region that becomes no-go zone.  Currently based off ad-hoc 
        ### assumptions for the angular reach  of a probe shaft from a particular valve.
        for i in range(0, bar-1, 2):
            xe = self.xpos[i+1]
            xorg = self.xpos[i]
            ye = self.ypos[i+1]
            yorg = self.ypos[i]

            if self.hand == 1:
                C = (yorg)/(xorg + 250)
                xvo = (-(500*C*C) + np.sqrt((C*C*500)**2 -
                       4*(C*C*C*C-1)*(250**2)))/(2*(C*C+1))
                yvo = C*(xvo+250)

                C = ye/(xe + 250)
                xve = (-(C*C*500) + np.sqrt((C*C*500)**2 -
                       4*(C*C*C*C-1)*(250**2)))/(2*(C*C+1))
                yve = C*(xve+250)

            if self.hand == 0:
                C = (yorg)/(xorg - 250)
                xvo = ((C*C*500) - np.sqrt((C*C*500)**2 -
                       4*(C*C*C*C-1)*(250**2)))/(2*(C*C+1))
                yvo = C*(xvo-250)

                C = (ye)/(xe - 250)
                xve = ((C*C*500) - np.sqrt((C*C*500)**2 -
                       4*(C*C*C*C-1)*(250**2)))/(2*(C*C+1))
                yve = C*(xve-250)

            barlist.append([(xorg, yorg, self.z1), (xe, ye, self.z1),
                           (xvo, yvo, self.z1), (xve, yve, self.z1)])

        barlist = np.array(barlist)/5
        self.barlist = barlist

        if mode == "line":
            self.get_positionsline()
            # self.update_graph(self.poslist)

        elif mode == "rect":
            self.get_positionsrect()
            # self.update_graph(self.poslist)

        elif mode == "polyline":
            self.get_positionspoly()
            # self.update_graph(self.poslist)

        elif mode == 'circle':
            self.get_positionscircle()

        elif mode == 'ellipse':
            self.get_positionsellipse()

    def get_positionsrect(self):
        ''' point generator for rectangular/cuboidal shapes. Defined by corner vertices'''
        bar = self.bar
        poslist = []

        if self.grid == 'rect':
            for i in range(bar, len(self.xpos)-1, 2):
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

                zvals = np.linspace(self.z1, self.z2, linvalz+1)
                xpos = np.linspace(xmin, xmax, linvalx+1)
                ypos = np.linspace(ymin, ymax, linvaly+1)

                positions = []
                for z in range(0, len(zvals)):
                    for x in range(0, len(xpos)):
                        for y in range(0, len(ypos)):
                            positions.append([xpos[x], ypos[y], zvals[z]])

                poslist.extend(positions)
            self.poslist = poslist

        if self.grid == 'circle':

            xpos = []
            ypos = []
            dr = self.nx
            dtheta = self.ny/5
            nz = self.nz
            for i in range(bar, len(self.xpos)-1, 2):
                xmax = max([self.xpos[i+1], self.xpos[i]])
                xmin = min([self.xpos[i+1], self.xpos[i]])
                ymax = max([self.ypos[i+1], self.ypos[i]])
                ymin = min([self.ypos[i+1], self.ypos[i]])

                linvalz = abs(math.floor((self.z2-self.z1)/(nz)))
                if self.centers == '':
                    cx = (xmax+xmin)/2
                    cy = (ymax+ymin)/2
                else:
                    str1 = self.centers
                    str1 = np.array(str1.replace('(', '').replace(')', '').split(
                        ','), dtype=float).reshape(-1, 3)
                    xs = [5*x[0] for x in str1]
                    ys = [5*x[1] for x in str1]
                    zs = [5*x[2] for x in str1]
                    cx = xs[i/2]
                    cy = ys[i/2]
                    cz = zs[i/2]
        # NEED TO RECALCULATE POINT GENERATING PARAMETERS TO GET APPROPRIATE ONES WITHIN THE REGION.
                zvals = np.linspace(self.z1, self.z2, linvalz+1)
                xpos = np.append(xpos, cx)
                ypos = np.append(ypos, cy)

                r = 0.5*(np.sqrt((xmax-xmin)**2 + (ymax-ymin)**2))

                linval = math.floor(r/(dr))

                thetavals = np.linspace(0, 1, math.floor(360/dtheta) + 1)
                parvals = np.linspace(0, 1, linval+1)
                positions = []
                # first start point already initialized in array.
                for t in parvals[1:]:
                    # Other start points are incorporated as the end points of previous segment.
                    for z in thetavals[1:]:
                        xval = cx + t*r*np.cos(z*2*np.pi)
                        yval = cy + t*r*np.sin(z*2*np.pi)

                        if (xval > xmax) or xval < xmin or yval > ymax or yval < ymin:
                            pass
                        else:
                            xpos = np.append(xpos, xval)
                            ypos = np.append(ypos, yval)

                for z in range(0, len(zvals)):
                    zpos = z*np.ones(len(xpos))
                    positions = list(zip(xpos, ypos, zpos))
                    poslist = poslist + positions

            self.poslist = poslist

                
        if self.grid == 'sphere':

           
            dr = self.nx
            dtheta = self.ny/5
            dphi = self.nz/5
            for i in range(bar, len(self.xpos)-1, 2):
                xmax = max([self.xpos[i+1], self.xpos[i]])
                xmin = min([self.xpos[i+1], self.xpos[i]])
                ymax = max([self.ypos[i+1], self.ypos[i]])
                ymin = min([self.ypos[i+1], self.ypos[i]])
                zmax = max([self.z1,self.z2])
                zmin = min([self.z1,self.z2])
                
                if self.centers == '':
                    cx = (xmax+xmin)/2
                    cy = (ymax+ymin)/2
                    cz = (zmax+zmin)/2
                else:
                    str1 = self.centers
                    str1 = np.array(str1.replace('(', '').replace(')', '').split(
                        ','), dtype=float).reshape(-1, 3)
                    xs = [5*x[0] for x in str1]
                    ys = [5*x[1] for x in str1]
                    zs = [5*x[2] for x in str1]
                    cx = xs[i/2]
                    cy = ys[i/2]
                    cz = zs[i/2]
        # NEED TO RECALCULATE POINT GENERATING PARAMETERS TO GET APPROPRIATE ONES WITHIN THE REGION.
                
               
                r = (np.sqrt((xmax-xmin)**2 + (ymax-ymin)**2) + (zmax-zmin)**2)

                linval = math.floor(r/(dr))

                thetavals = np.linspace(0, 1, math.floor(360/dtheta) + 1)
                phivals = np.linspace(0,1,math.floor(180/dphi)+1)
                parvals = np.linspace(0, 1, linval+1)
                positions = [[cx,cy,cz]]
                # first start point already initialized in array.
                for t in parvals[1:]:
                    # Other start points are incorporated as the end points of previous segment.
                    for z in thetavals[1:]:
                        for p in phivals[1:]:
                            xval = cx + t*r*np.cos(z*2*np.pi)*np.sin(p*np.pi)
                            yval = cy + t*r*np.sin(z*2*np.pi)*np.sin(p*np.pi)
                            zval = cz + t*r*np.cos(p*np.pi)
                        if (xval > xmax) or xval < xmin or yval > ymax or yval < ymin or zval > zmax or zval < zmin:
                            pass
                        else:
                            positions.append([xval, yval, zval])

                poslist = poslist + positions

            self.poslist = poslist

        
        if self.grid == 'ellipse':
            
            xpos = [self.xpos[bar]]
            ypos = [self.ypos[bar]]
            dr = self.nx
            dtheta = self.ny/5
            nz = self.nz
            linvalz = abs(math.floor((self.z2-self.z1)/(nz)))
            zvals = np.linspace(self.z1, self.z2, linvalz+1)

            for i in range(bar, len(self.xpos)-1, 2):

                xposi = self.xpos[i]
                xposi2 = self.xpos[i+1]

                yposi = self.ypos[i]
                yposi2 = self.ypos[i+1]

                a = np.abs(xposi2 - xposi)
                b = np.abs(yposi2-yposi)
                cx = (xposi + xposi2)/2
                cy = (yposi + yposi2)/2
                # zposi = zs[i]
                # zposi2 =zs[i+1]

                linval = math.floor((min([a, b]))/(dr))

                thetavals = np.linspace(0, 1, math.floor(360/dtheta) + 1)
                parvals = np.linspace(0, 1, linval+1)

                for t in parvals[1:]:
                    for z in thetavals[1:]:
                        xval = cx + t*a*np.cos(z*2*np.pi)
                        yval = cy + t*b*np.sin(z*2*np.pi)

                        xpos = np.append(xpos, xval)
                        ypos = np.append(ypos, yval)

            for z in range(0, len(zvals)):
                zpos = z*np.ones(len(xpos))
                positions = list(zip(xpos, ypos, zpos))
                poslist = poslist + positions
                

    def get_positionsline(self):
        ''' point generator for lines'''

        poslist = []
        bar = self.bar
        xs = self.xpos
        ys = self.ypos

        nz = self.nz

        linvalz = abs(math.floor((self.z2-self.z1)/(nz)))
        zvals = np.linspace(self.z1, self.z2, linvalz+1)
        xpos = []
        ypos = []
#            zpos = [zs[0]]

        for i in range(bar, len(xs)-1, 2):

            # general idea for motion list- user gave end points of line segments.
            # each point is essentially a location in the array. Get distance between the
            # two array points.    #Get an equation of the line joining two points in the array.
            # Get real coordinates of the point on this line at every
            #  'res' distance.

            # the coordinates of the two end points of line segment

            xposi = xs[i]
            xposi2 = xs[i+1]

            yposi = ys[i]
            yposi2 = ys[i+1]

            # zposi = zs[i]
            # zposi2 =zs[i+1]
            res = (self.nx**2 + self.ny**2)**0.5
            length = ((xposi2-xposi)**2 + (yposi2-yposi)**2)**0.5
            linval = math.floor(length/(res))

            parvals = np.linspace(0, 1, linval+1)

            for t in parvals:

                xval = xposi + t*(xposi2 - xposi)
                yval = yposi + t*(yposi2 - yposi)
                # zval = zposi + t*(zposi2 - zposi)
                xpos = np.append(xpos, xval)
                ypos = np.append(ypos, yval)

        for z in range(0, len(zvals)):
            zpos = z*np.ones(len(xpos))
            positions = list(zip(xpos, ypos, zpos))
            poslist = poslist + positions

        self.poslist = poslist

    def get_positionspoly(self):
        ''' point generator for polygonal lines. Currently defaults to not closing shape'''

        poslist = []
        if self.closeit == True:
                    index = 1
        elif self.closeit == False:
                    index = 0
        bar = int(self.bar/2)
        xs = np.delete(self.xpos, -1)
        ys = np.delete(self.ypos, -1)

        xs = xs[1::2]
        ys = ys[1::2]
        xpos = [xs[bar]]
        ypos = [ys[bar]]
        
        if self.closeit == True:
            p = QPainter(self.pixmap())

            p.setPen(QPen(QColor(Qt.black), self.config['size'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            p.setBrush(QBrush(QColor(Qt.black)))
        
            p.drawLine(QPointF(xs[-1]+300, -ys[-1]+300),
                   QPointF(xs[0]+300, -ys[0]+300))

        for i in range(bar-index, len(xs)-1):
            xposi = xs[i]
            xposi2 = xs[i+1]

            yposi = ys[i]
            yposi2 = ys[i+1]

            res = (self.nx**2 + self.ny**2)**0.5
            length = ((xposi2-xposi)**2 + (yposi2-yposi)**2)**0.5
            linval = math.floor(length/(res))

            parvals = np.linspace(0, 1, linval+1)

            for t in parvals[1:]:

                xval = xposi + t*(xposi2 - xposi)
                yval = yposi + t*(yposi2 - yposi)
                # zval = zposi + t*(zposi2 - zposi)
                xpos = np.append(xpos, xval)
                ypos = np.append(ypos, yval)

        nz = self.nz

        linvalz = abs(math.floor((self.z2-self.z1)/(nz)))
        zvals = np.linspace(self.z1, self.z2, linvalz+1)

        for z in range(0, len(zvals)):
            zpos = z*np.ones(len(xpos))
            positions = list(zip(xpos, ypos, zpos))
            poslist = poslist + positions

        self.poslist = poslist

    def get_positionscircle(self):
        ''' point generator for circular/cylindrical shapes.
        Circles are defined by point at centrre and random point on the circular edge.'''

        poslist = []
        bar = self.bar
        xs = self.xpos
        ys = self.ypos

        if self.grid == 'rect':
            for i in range(bar, len(self.xpos)-1, 2):

                xposi2 = self.xpos[i+1]
                xposi = self.xpos[i]
                yposi2 = self.ypos[i+1]
                yposi = self.ypos[i]

                r = np.sqrt((xposi - xposi2)**2 + (yposi-yposi2)**2)
                nx = self.nx
                ny = self.ny
                nz = self.nz

                if self.centers == '':
                    cx = xposi
                    cy = yposi
                else:
                    str1 = self.centers
                    str1 = np.array(str1.replace('(', '').replace(')', '').split(
                        ','), dtype=float).reshape(-1, 3)
                    xs = [5*x[0] for x in str1]
                    ys = [5*x[1] for x in str1]
                    zs = [5*x[2] for x in str1]
                    cx = xs[i]
                    cy = ys[i]
                    cz = zs[i]

                xmax = cx + r
                xmin = cx - r
                ymax = cy + r
                ymin = cy - r

                linvalz = abs(math.floor((self.z2-self.z1)/(nz)))

                linvalx = abs(math.floor((xmax-xmin)/(nx)))
                linvaly = abs(math.floor((ymax-ymin)/(ny)))

                zvals = np.linspace(self.z1, self.z2, linvalz+1)
                xpos = np.linspace(xmin, xmax, linvalx+1)
                ypos = np.linspace(ymin, ymax, linvaly+1)

                positions = []
                for z in range(0, len(zvals)):
                    for x in range(0, len(xpos)):
                        for y in range(0, len(ypos)):
                            r1 = np.sqrt((cx-xpos[x])**2 + (cy-ypos[y])**2)
                            if r1 <= r:
                                positions.append([xpos[x], ypos[y], zvals[z]])
                            else:
                                pass

                poslist.extend(positions)
            self.poslist = poslist

        if self.grid == 'circle':

            dr = self.nx
            dtheta = self.ny/5
            nz = self.nz

            linvalz = abs(math.floor((self.z2-self.z1)/(nz)))
            zvals = np.linspace(self.z1, self.z2, linvalz+1)
            xpos = [xs[bar]]
            ypos = [ys[bar]]
#                
            for i in range(bar, len(xs)-1, 2):

                xposi = xs[i]
                xposi2 = xs[i+1]

                yposi = ys[i]
                yposi2 = ys[i+1]

                r = np.sqrt((xposi - xposi2)**2 + (yposi-yposi2)**2)
                # zposi = zs[i]
                # zposi2 =zs[i+1]

                linval = math.floor(r/(dr))

                thetavals = np.linspace(0, 1, math.floor(360/dtheta) + 1)
                parvals = np.linspace(0, 1, linval+1)

                for t in parvals[1:]:
                    for z in thetavals[1:]:
                        xval = xposi + t*r*np.cos(z*2*np.pi)
                        yval = yposi + t*r*np.sin(z*2*np.pi)

                        xpos = np.append(xpos, xval)
                        ypos = np.append(ypos, yval)

            for z in range(0, len(zvals)):
                zpos = z*np.ones(len(xpos))
                positions = list(zip(xpos, ypos, zpos))
                poslist = poslist + positions

            self.poslist = poslist

        if self.grid == 'sphere':

            dr = self.nx
            dtheta = self.ny/5
            dphi = self.nz/5
            zmax = max([self.z1,self.z2])
            zmin = min([self.z1,self.z2])

            for i in range(bar, len(xs)-1, 2):

                xposi = xs[i]
                xposi2 = xs[i+1]

                yposi = ys[i]
                yposi2 = ys[i+1]

                rc = np.sqrt((xposi - xposi2)**2 + (yposi-yposi2)**2 )
                
                if self.centers == '':
                    cx = xposi
                    cy = yposi
                    cz = (zmax+zmin)/2
                else:
                    str1 = self.centers
                    str1 = np.array(str1.replace('(', '').replace(')', '').split(
                        ','), dtype=float).reshape(-1, 3)
                    xs = [5*x[0] for x in str1]
                    ys = [5*x[1] for x in str1]
                    zs = [5*x[2] for x in str1]
                    cx = xs[i/2]
                    cy = ys[i/2]
                    cz = zs[i/2]
                
                xmax = cx + rc
                xmin = cx - rc
                ymax = cy + rc
                ymin = cy -rc
                
                r = 0.5*(np.sqrt((xmax-xmin)**2 + (ymax-ymin)**2) + (zmax-zmin)**2)

                linval = math.floor(r/(dr))

                thetavals = np.linspace(0, 1, math.floor(360/dtheta) + 1)
                phivals = np.linspace(0,1,math.floor(180/dphi)+1)
                parvals = np.linspace(0, 1, linval+1)
                positions = [[cx,cy,cz]]
                # first start point already initialized in array.
                for t in parvals[1:]:
                    # Other start points are incorporated as the end points of previous segment.
                    for z in thetavals[1:]:
                        for p in phivals[1:]:
                            xval = cx + t*r*np.cos(z*2*np.pi)*np.sin(p*np.pi)
                            yval = cy + t*r*np.sin(z*2*np.pi)*np.sin(p*np.pi)
                            zval = cz + t*r*np.cos(p*np.pi)
                        if (xval-cx)**2 + (yval-cy)**2 > rc**2 or zval > zmax or zval < zmin:
                            pass
                        else:
                            positions.append([xval, yval, zval])

                poslist = poslist + positions

            self.poslist = poslist

        if self.grid == 'ellipse':

            dr = self.nx
            dtheta = self.ny/5
            nz = self.nz

            linvalz = abs(math.floor((self.z2-self.z1)/(nz)))
            zvals = np.linspace(self.z1, self.z2, linvalz+1)
            xpos = [xs[bar]]
            ypos = [ys[bar]]
#                zpos = [zs[0]]

            for i in range(bar, len(xs)-1, 2):

                xposi = xs[i]
                xposi2 = xs[i+1]

                yposi = ys[i]
                yposi2 = ys[i+1]

                r = np.sqrt((xposi - xposi2)**2 + (yposi-yposi2)**2)
                # zposi = zs[i]
                # zposi2 =zs[i+1]

                linval = math.floor(r/(dr))

                thetavals = np.linspace(0, 1, math.floor(360/dtheta) + 1)
                parvals = np.linspace(0, 1, linval+1)

                for t in parvals[1:]:
                    for z in thetavals[1:]:
                        xval = xposi + t*r*np.cos(z*2*np.pi)
                        yval = yposi + t*r*np.sin(z*2*np.pi)

                        xpos = np.append(xpos, xval)
                        ypos = np.append(ypos, yval)

            for z in range(0, len(zvals)):
                zpos = z*np.ones(len(xpos))
                positions = list(zip(xpos, ypos, zpos))
                poslist = poslist + positions

            self.poslist = poslist
   
    
    def get_positionsellipse(self):
        ''' point generator for elliptical shapes. 
        Ellipse defined by circumscribing rectangle'''


        poslist = []
        bar = self.bar
        xs = self.xpos
        ys = self.ypos

        nz = self.nz
        linvalz = abs(math.floor((self.z2-self.z1)/(nz)))
        zvals = np.linspace(self.z1, self.z2, linvalz+1)

        if self.grid == 'ellipse':

            #                 zpos = [zs[0]]
            dr = self.nx
            dtheta = self.ny/5

            for i in range(bar, len(xs)-1, 2):

                xposi = xs[i]
                xposi2 = xs[i+1]

                yposi = ys[i]
                yposi2 = ys[i+1]

                a = np.abs(xposi2 - xposi)/2
                b = np.abs(yposi2-yposi)/2
                if self.centers == '':
                    cx = (xposi + xposi2)/2
                    cy = (yposi + yposi2)/2
                else:
                    str1 = self.centers
                    str1 = np.array(str1.replace('(', '').replace(')', '').split(
                        ','), dtype=float).reshape(-1, 3)
                    xs = [5*x[0] for x in str1]
                    ys = [5*x[1] for x in str1]
                    zs = [5*x[2] for x in str1]
                    cx = xs[i]
                    cy = ys[i]
                    cz = zs[i]
                xpos = [cx]
                ypos = [cy]
                linval = math.floor((min([a, b]))/(dr))

                thetavals = np.linspace(0, 1, math.floor(360/dtheta) + 1)
                parvals = np.linspace(0, 1, linval+1)

                for t in parvals[1:]:
                    for z in thetavals[1:]:
                        xval = cx + t*a*np.cos(z*2*np.pi)
                        yval = cy + t*b*np.sin(z*2*np.pi)
                        if ((xval-cx)/a)**2 + ((yval-cy)/b)**2 <= 1:
                            xpos = np.append(xpos, xval)
                            ypos = np.append(ypos, yval)

            for z in range(0, len(zvals)):
                zpos = z*np.ones(len(xpos))
                positions = list(zip(xpos, ypos, zpos))
                poslist = poslist + positions

            self.poslist = poslist

        if self.grid == 'rect':
            for i in range(bar, len(self.xpos)-1, 2):
                xmax = self.xpos[i+1]
                xmin = self.xpos[i]
                ymax = self.ypos[i+1]
                ymin = self.ypos[i]
                nx = self.nx
                ny = self.ny
                nz = self.nz
                a = np.abs(xmax - xmin)/2
                b = np.abs(ymax-ymin)/2
                if self.centers == '':
                    cx = (xmax + xmin)/2
                    cy = (ymax + ymin)/2
                else:
                    str1 = self.centers
                    str1 = np.array(str1.replace('(', '').replace(')', '').split(
                        ','), dtype=float).reshape(-1, 3)
                    xs = [5*x[0] for x in str1]
                    ys = [5*x[1] for x in str1]
                    zs = [5*x[2] for x in str1]
                    cx = xs[i]
                    cy = ys[i]
                    cz = zs[i]
                linvalz = abs(math.floor((self.z2-self.z1)/(nz)))

                linvalx = abs(math.floor((xmax-xmin)/(nx)))
                linvaly = abs(math.floor((ymax-ymin)/(ny)))

                zvals = np.linspace(self.z1, self.z2, linvalz+1)
                xpos = np.linspace(xmin, xmax, linvalx+1)
                ypos = np.linspace(ymin, ymax, linvaly+1)

                positions = []
                for z in range(0, len(zvals)):
                    for x in range(0, len(xpos)):
                        for y in range(0, len(ypos)):
                            if (((xpos[x]-cx)/a)**2 + ((ypos[y]-cy)/b)**2 <= 1):
                                positions.append([xpos[x], ypos[y], zvals[z]])
                            else:
                                pass

                poslist.extend(positions)
            self.poslist = poslist

        if self.grid == 'circle':
            dr = self.nx
            dtheta = self.ny/5
            
            for i in range(bar, len(xs)-1, 2):

                xposi = xs[i]
                xposi2 = xs[i+1]

                yposi = ys[i]
                yposi2 = ys[i+1]
                a = np.abs(xposi - xposi2)/2
                b = np.abs(yposi-yposi2)/2
                r = np.sqrt((xposi2 - xposi)**2 + (yposi -yposi2)**2)*0.5

                if self.centers == '':
                    cx = (xposi + xposi2)/2
                    cy = (yposi + yposi2)/2
                else:
                    str1 = self.centers
                    str1 = np.array(str1.replace('(', '').replace(')', '').split(
                        ','), dtype=float).reshape(-1, 3)
                    xs = [5*x[0] for x in str1]
                    ys = [5*x[1] for x in str1]
                    zs = [5*x[2] for x in str1]
                    cx = xs[i]
                    cy = ys[i]
                    cz = zs[i]
                xpos = [cx]
                ypos = [cy]
                linval = math.floor(r/dr)

                thetavals = np.linspace(0, 1, math.floor(360/dtheta) + 1)
                parvals = np.linspace(0, 1, linval+1)

                for t in parvals[1:]:
                    for z in thetavals[1:]:
                        xval = cx + t*r*np.cos(z*2*np.pi)
                        yval = cy + t*r*np.sin(z*2*np.pi)
                        if ((xval-cx)/a)**2 + ((yval-cy)/b)**2 <= 1:
                            xpos = np.append(xpos, xval)
                            ypos = np.append(ypos, yval)

            for z in range(0, len(zvals)):
                zpos = z*np.ones(len(xpos))
                positions = list(zip(xpos, ypos, zpos))
                poslist = poslist + positions

            self.poslist = poslist
            
        if self.grid == 'sphere':

            dr = self.nx
            dtheta = self.ny/5
            dphi = self.nz/5
            zmax = max([self.z1,self.z2])
            zmin = min([self.z1,self.z2])

            for i in range(bar, len(xs)-1, 2):

                xposi = xs[i]
                xposi2 = xs[i+1]

                yposi = ys[i]
                yposi2 = ys[i+1]

                
                
                a = np.abs(xposi - xposi2)/2
                b = np.abs(yposi-yposi2)/2
                r = np.sqrt((xposi2 - xposi)**2 + (yposi -yposi2)**2 + (zmax-zmin))*0.5

                if self.centers == '':
                    cx = (xposi + xposi2)/2
                    cy = (yposi + yposi2)/2
                    cz = (self.z1+self.z2)/2
                else:
                    str1 = self.centers
                    str1 = np.array(str1.replace('(', '').replace(')', '').split(
                        ','), dtype=float).reshape(-1, 3)
                    xs = [5*x[0] for x in str1]
                    ys = [5*x[1] for x in str1]
                    zs = [5*x[2] for x in str1]
                    cx = xs[i]
                    cy = ys[i]
                    cz = zs[i]
        

                linval = math.floor(r/(dr))

                thetavals = np.linspace(0, 1, math.floor(360/dtheta) + 1)
                phivals = np.linspace(0,1,math.floor(180/dphi)+1)
                parvals = np.linspace(0, 1, linval+1)
                positions = [[cx,cy,cz]]
                # first start point already initialized in array.
                for t in parvals[1:]:
                    # Other start points are incorporated as the end points of previous segment.
                    for z in thetavals[1:]:
                        for p in phivals[1:]:
                            xval = cx + t*r*np.cos(z*2*np.pi)*np.sin(p*np.pi)
                            yval = cy + t*r*np.sin(z*2*np.pi)*np.sin(p*np.pi)
                            zval = cz + t*r*np.cos(p*np.pi)
                        if ((xval-cx)/a)**2 + ((yval-cy)/b)**2 > 1 or zval > zmax or zval < zmin:
                            pass
                        else:
                            positions.append([xval, yval, zval])

                poslist = poslist + positions

            self.poslist = poslist
         
            
    

    def checklist(self, arg):
        '''Final verification routine to check no point is in a no-go region or an unreachable 
        region.
        Must be run to save the config/text coordinate files. 
        '''
        # self.set_status()
        xs = [x[0] for x in self.poslist]
        ys = [x[1] for x in self.poslist]

        barlist = self.barlist*5

        for i in range(0, len(xs)):
            dist = ((xs[i])**2 + (ys[i])**2)**0.5

            if (dist > 250):
                arg.saveButton.setEnabled(False)

                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Error")
                msg.setInformativeText(
                    'Some designated points are outside of the machine!')
                msg.setWindowTitle("Error")
                msg.exec_()
                return

            if self.hand == 0:
                if (ys[i] - 0 - (xs[i] - 250) < 0):
                    arg.saveButton.setEnabled(False)
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText("Error")
                    msg.setInformativeText(
                        'Some designated points are outside of reach!!')
                    msg.setWindowTitle("Error")
                    msg.exec_()
                    return
                elif (ys[i] - 0 + (xs[i] - 250) > 0):
                    arg.saveButton.setEnabled(False)
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText("Error")
                    msg.setInformativeText(
                        'Some designated points are outside of reach!')
                    msg.setWindowTitle("Error")
                    msg.exec_()
                    return

                # posgroup is [(xorg,y,z),(xe),(xvo),(xve)]
                for posgroup in barlist:
                    if posgroup[0][0]-posgroup[1][0] == 0:
                        m1 = 1
                    else:
                        m1 = (posgroup[0][1]-posgroup[1][1]) / \
                            (posgroup[0][0]-posgroup[1][0])
                    m2 = (posgroup[0][1] - posgroup[2][1]) / \
                        (posgroup[0][0]-posgroup[2][0])
                    m3 = (posgroup[1][1] - posgroup[3][1]) / \
                        (posgroup[1][0]-posgroup[3][0])

                    if (
                        ((ys[i] - m1*(xs[i] - posgroup[0][0]) - posgroup[0][1] > 0 and m1 > 0)
                         or (ys[i] - m1*(xs[i] - posgroup[0][0]) - posgroup[0][1] < 0 and m1 < 0))

                        and (
                            ((ys[i] - m2*(xs[i]-posgroup[0][0]) - posgroup[0][1] < 0) and (ys[i] - m3*(
                                xs[i] + m3*posgroup[1][0]) - posgroup[1][1] > 0) and (posgroup[0][1] > posgroup[1][1]))
                            or
                            ((ys[i] - m2*(xs[i]-posgroup[0][0]) - posgroup[0][1] > 0) and (ys[i] - m3*(
                                xs[i] + m3*posgroup[1][0]) - posgroup[1][1] < 0) and (posgroup[0][1] < posgroup[1][1]))
                        )



                    ):
                        arg.saveButton.setEnabled(False)
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Critical)
                        msg.setText("Error")
                        msg.setInformativeText(
                            'Some designated points are in No-go zone!!')
                        msg.setWindowTitle("Error")
                        msg.exec_()
                        return

            if self.hand == 1:

                if (ys[i] - 0 + (xs[i] + 250) < 0):
                    arg.saveButton.setEnabled(False)
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText("Error")
                    msg.setInformativeText(
                        'Designated point is outside of reach!!')
                    msg.setWindowTitle("Error")
                    msg.exec_()
                    return

                elif (ys[i] - 0 - (xs[i] + 250) > 0):

                    arg.saveButton.setEnabled(False)
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText("Error")
                    msg.setInformativeText(
                        'Designated point is outside of reach!')
                    msg.setWindowTitle("Error")
                    msg.exec_()
                    return

                # posgroup is [(xorg,y,z),(xe),(xvo),(xve)]
                for posgroup in barlist:
                    if posgroup[0][0]-posgroup[1][0] == 0:
                        m1 = 1
                    else:
                        m1 = (posgroup[0][1]-posgroup[1][1]) / \
                            (posgroup[0][0]-posgroup[1][0])
                    m2 = (posgroup[0][1] - posgroup[2][1]) / \
                        (posgroup[0][0]-posgroup[2][0])
                    m3 = (posgroup[1][1] - posgroup[3][1]) / \
                        (posgroup[1][0]-posgroup[3][0])

                    if (
                        ((ys[i] - m1*(xs[i] - posgroup[0][0]) - posgroup[0][1] > 0 and m1 < 0)
                         or (ys[i] - m1*(xs[i] - posgroup[0][0]) - posgroup[0][1] < 0 and m1 > 0))

                        and (
                            ((ys[i] - m2*(xs[i]-posgroup[0][0]) - posgroup[0][1] < 0) and (ys[i] - m3*(
                                xs[i] + m3*posgroup[1][0]) - posgroup[1][1] > 0) and (posgroup[0][1] > posgroup[1][1]))
                            or
                            ((ys[i] - m2*(xs[i]-posgroup[0][0]) - posgroup[0][1] > 0) and (ys[i] - m3*(
                                xs[i] + m3*posgroup[1][0]) - posgroup[1][1] < 0) and (posgroup[0][1] < posgroup[1][1]))
                        )



                    ):
                        arg.saveButton.setEnabled(False)
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Critical)
                        msg.setText("Error")
                        msg.setInformativeText(
                            'Some designated points are in No-go zone!!')
                        msg.setWindowTitle("Error")
                        msg.exec_()
                        return

        arg.saveButton.setEnabled(True)

    def coordEnter(self, arg, n =0):
        '''massive function, should probably be restructured, rewritten? 
        Same functionality as print_position() + get_*mode*_positions(), 
        Used when precise coordinates are fed by the user to the module.
        '''
        res = min(self.nx, self.ny, self.nz)
        bar = arg.barcord.text()
        barlist = []
        p = QPainter(self.pixmap())
        p.setPen(QPen(QColor(Qt.red), self.config['size'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.setBrush(QBrush(QColor(Qt.red)))
        if n == 0:
            str1 = arg.coordinates.text()
            # split the string by , in order to get an array
            str1 = np.array(str1.replace('(', '').replace(')', '').split(','), dtype=float).reshape(-1, 3)
        else:
            str1 = n
            str1 = np.array(str1.replace('(', '').replace(')', '').split(','), dtype=float).reshape(-1, 3)

            
        if bar[0] == '(':
            bar = np.array(bar.replace('(', '').replace(')', '').split(
                ','), dtype=float).reshape(-1, 3)
            xs = [5*x[0] for x in bar]
            ys = [5*x[1] for x in bar]
            zs = [5*x[2] for x in bar]
      

            for i in range(0, len(xs)-1, 2):
                xe = xs[i+1]
                xorg = xs[i]
                ye = ys[i+1]
                yorg = ys[i]

                if self.hand == 1:
                    C = (yorg)/(xorg + 250)
                    xvo = (-(500*C*C) + np.sqrt((C*C*500)**2 -
                           4*(C*C*C*C-1)*(250**2)))/(2*(C*C+1))
                    yvo = C*(xvo+250)

                    C = ye/(xe + 250)
                    xve = (-(C*C*500) + np.sqrt((C*C*500)**2 -
                           4*(C*C*C*C-1)*(250**2)))/(2*(C*C+1))
                    yve = C*(xve+250)

                if self.hand == 0:
                    C = (yorg)/(xorg - 250)
                    xvo = ((C*C*500) - np.sqrt((C*C*500)**2 -
                           4*(C*C*C*C-1)*(250**2)))/(2*(C*C+1))
                    yvo = C*(xvo-250)

                    C = (ye)/(xe - 250)
                    xve = ((C*C*500) - np.sqrt((C*C*500)**2 -
                           4*(C*C*C*C-1)*(250**2)))/(2*(C*C+1))
                    yve = C*(xve-250)

                p.drawLine(QPointF(xorg+300, -yorg+300),
                           QPointF(xvo+300, -yvo+300))
                p.drawLine(QPointF(xe+300, -ye+300),
                           QPointF(xve+300, -yve+300))

                p.setPen(QPen(QColor(
                    '#800000'), self.config['size'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                p.drawLine(QPointF(xorg+300, -yorg+300),
                           QPointF(xe+300, -ye+300))

                barlist.append([(xorg, yorg, self.z1), (xe, ye, self.z1),
                               (xvo, yvo, self.z1), (xve, yve, self.z1)])

                barlist = np.array(barlist)/5
            self.barlist = barlist

        if self.mode == 'polyline':
  
            try:

                xs = [5*x[0] for x in str1]
                ys = [5*x[1] for x in str1]
                zs = [5*x[2] for x in str1]
                xpos = [xs[0]]
                ypos = [ys[0]]
                zpos = [zs[0]]
                self.xpos = xs
                self.ypos = ys
                self.zpos = zs
                p.setPen(QPen(
                    QColor(Qt.black), self.config['size'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                p.setBrush(QBrush(QColor(Qt.black)))
                
                if self.closeit == True:
                    index = -1
                elif self.closeit == False:
                    index = 0
                
                
                for i in range(index, len(xs)-1):
                    p.drawLine(QPointF(xs[i]+300, -ys[i]+300),
                               QPointF(xs[i+1]+300, -ys[i+1]+300))

                for i in range(index, len(xs)-1):

                    xposi = xs[i]
                    xposi2 = xs[i+1]

                    yposi = ys[i]
                    yposi2 = ys[i+1]

                    zposi = zs[i]
                    zposi2 = zs[i+1]

                    length = ((xposi2-xposi)**2 + (yposi2-yposi)
                              ** 2 + (zposi2-zposi)**2)**0.5
                    linval = math.floor(length/(res))

                    parvals = np.linspace(0, 1, linval+1)

                    for t in parvals[1:]:

                        xval = xposi + t*(xposi2 - xposi)
                        yval = yposi + t*(yposi2 - yposi)
                        zval = zposi + t*(zposi2 - zposi)
                        xpos = np.append(xpos, xval)
                        ypos = np.append(ypos, yval)
                        zpos = np.append(zpos, zval)

                positions = list(zip(xpos, ypos, zpos))
                self.poslist = positions

            except ValueError:
                QMessageBox.about(
                    self, "Error", "Position should be valid numbers.")

        elif self.mode == 'line':
           
            try:

                xs = [5*x[0] for x in str1]
                ys = [5*x[1] for x in str1]
                zs = [5*x[2] for x in str1]
                xpos = [xs[0]]
                ypos = [ys[0]]
                zpos = [zs[0]]
                self.xpos = xs
                self.ypos = ys
                self.zpos = zs
                p.setPen(QPen(
                    QColor(Qt.black), self.config['size'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                p.setBrush(QBrush(QColor(Qt.black)))

                for i in range(0, len(xs)-1, 2):
                    p.drawLine(QPointF(xs[i]+300, -ys[i]+300),
                               QPointF(300+xs[i+1], -ys[i+1]+300))

                for i in range(0, len(xs)-1, 2):

                    xposi = xs[i]
                    xposi2 = xs[i+1]

                    yposi = ys[i]
                    yposi2 = ys[i+1]

                    zposi = zs[i]
                    zposi2 = zs[i+1]

                    length = ((xposi2-xposi)**2 + (yposi2-yposi)
                              ** 2 + (zposi2-zposi)**2)**0.5
                    linval = math.floor(length/(res))

                    parvals = np.linspace(0, 1, linval+1)

                    for t in parvals[1:]:

                        xval = xposi + t*(xposi2 - xposi)
                        yval = yposi + t*(yposi2 - yposi)
                        zval = zposi + t*(zposi2 - zposi)
                        xpos = np.append(xpos, xval)
                        ypos = np.append(ypos, yval)
                        zpos = np.append(zpos, zval)

                positions = list(zip(xpos, ypos, zpos))
                self.poslist = positions

            except ValueError:
                QMessageBox.about(
                    self, "Error", "Position should be valid numbers.")

        elif self.mode == 'rect':

            if self.grid == 'rect':
               
                try:

                    xs = [5*x[0] for x in str1]
                    ys = [5*x[1] for x in str1]
                    zs = [5*x[2] for x in str1]
                    self.xpos = xs
                    self.ypos = ys
                    self.zpos = zs
                    nx = self.nx
                    ny = self.ny
                    nz = self.nz
                    p.setPen(QPen(
                        QColor(Qt.black), self.config['size'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                    p.setBrush(QBrush(QColor(Qt.black)))
                    for i in range(0, len(xs)-1, 2):
                        p.drawRect(
                            QRectF(xs[i]+300, -ys[i]+300, xs[i+1]-xs[i], -ys[i+1]+ys[i]))

                        poslist = []
                        for i in range(0, len(self.xpos)-1, 2):
                            xmax = self.xpos[i+1]
                            xmin = self.xpos[i]
                            ymax = self.ypos[i+1]
                            ymin = self.ypos[i]
                            zmax = zs[i+1]
                            zmin = zs[i]

                            linvalz = abs(math.floor((zmax-zmin)/(nz)))

                            linvalx = abs(math.floor((xmax-xmin)/(nx)))
                            linvaly = abs(math.floor((ymax-ymin)/(ny)))

                            zvals = np.linspace(zmin, zmax, linvalz+1)
                            xpos = np.linspace(xmin, xmax, linvalx+1)
                            ypos = np.linspace(ymin, ymax, linvaly+1)

                            positions = []
                            for z in range(0, len(zvals)):
                                for x in range(0, len(xpos)):
                                    for y in range(0, len(ypos)):
                                        positions.append(
                                            [xpos[x], ypos[y], zvals[z]])

                        poslist.extend(positions)
                        # print(poslist)
                        self.poslist = poslist

                except ValueError:
                    QMessageBox.about(
                        self, "Error", "Position should be valid numbers.")

            if self.grid == 'circle':
               
                try:

                    xs = [5*x[0] for x in str1]
                    ys = [5*x[1] for x in str1]
                    zs = [5*x[2] for x in str1]
                    self.xpos = xs
                    self.ypos = ys
                    self.zpos = zs
                    dr = self.nx
                    dtheta = self.ny/5
                    nz = self.nz
                    p.setPen(QPen(
                        QColor(Qt.black), self.config['size'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                    p.setBrush(QBrush(QColor(Qt.black)))

                    xpos = []
                    ypos = []
                    poslist = []
                    for i in range(0, len(self.xpos)-1, 2):
                        p.drawRect(
                            QRectF(xs[i]+300, -ys[i]+300, xs[i+1]-xs[i], -ys[i+1]+ys[i]))
                        xmax = max([self.xpos[i+1], self.xpos[i]])
                        xmin = min([self.xpos[i+1], self.xpos[i]])
                        ymax = max([self.ypos[i+1], self.ypos[i]])
                        ymin = min([self.ypos[i+1], self.ypos[i]])
                        zmax = max([self.zpos[i+1], self.zpos[i]])
                        zmin = min([self.zpos[i+1], self.zpos[i]])

                        linvalz = abs(math.floor((zmax-zmin)/(nz)))

                        if self.centers == '':
                            cx = (xmax+xmin)/2
                            cy = (ymax+ymin)/2
                            cz = (zmax+zmin)/2
                        else:
                            str1 = self.centers
                            str1 = np.array(str1.replace('(', '').replace(')', '').split(
                                ','), dtype=float).reshape(-1, 3)
                            xs1 = [5*x[0] for x in str1]
                            ys1 = [5*x[1] for x in str1]
                            zs1 = [5*x[2] for x in str1]
                            cx = (xs1[i] + xs1[i+1])/2
                            cy = (ys1[i] + ys1[i+1])/2
                            cz = (zs1[i] + zs1[i+1])/2
                        # NEED TO RECALCULATE POINT GENERATING PARAMETERS TO GET APPROPRIATE ONES WITHIN THE REGION.
                        zvals = np.linspace(zmin, zmax, linvalz+1)

                        r = 0.5*(np.sqrt((xmax-xmin)**2 + (ymax-ymin)**2))

                        linval = math.floor(r/(dr))

                        thetavals = np.linspace(
                            0, 1, math.floor(360/dtheta) + 1)
                        parvals = np.linspace(0, 1, linval+1)
                        positions = []
                        for t in parvals[1:]:
                            for z in thetavals[1:]:
                                xval = cx + t*r*np.cos(z*2*np.pi)
                                yval = cy + t*r*np.sin(z*2*np.pi)

                                if (xval > xmax) or xval < xmin or yval > ymax or yval < ymin:
                                    pass
                                else:
                                    xpos = np.append(xpos, xval)
                                    ypos = np.append(ypos, yval)

                        for z in range(0, len(zvals)):
                            zpos = z*np.ones(len(xpos))
                            positions = list(zip(xpos, ypos, zpos))
                            poslist = poslist + positions
                        self.poslist = poslist

                except ValueError:
                    QMessageBox.about(
                        self, "Error", "Position should be valid numbers.")
      ###############NOT IMPLEMENTED$$$$$$$$$              
            if self.grid == 'ellipse':
               
                try:

                    xs = [5*x[0] for x in str1]
                    ys = [5*x[1] for x in str1]
                    zs = [5*x[2] for x in str1]
                    self.xpos = xs
                    self.ypos = ys
                    self.zpos = zs
                    dr = self.nx
                    dtheta = self.ny/5
                    nz = self.nz
                    p.setPen(QPen(
                        QColor(Qt.black), self.config['size'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                    p.setBrush(QBrush(QColor(Qt.black)))

                    xpos = []
                    ypos = []
                    poslist = []
                    for i in range(0, len(self.xpos)-1, 2):
                        p.drawRect(
                            QRectF(xs[i]+300, -ys[i]+300, xs[i+1]-xs[i], -ys[i+1]+ys[i]))
                       

                except ValueError:
                    QMessageBox.about(
                        self, "Error", "Position should be valid numbers.")


            if self.grid == 'sphere':
              
                try:

                    xs = [5*x[0] for x in str1]
                    ys = [5*x[1] for x in str1]
                    zs = [5*x[2] for x in str1]
                    self.xpos = xs
                    self.ypos = ys
                    self.zpos = zs
                    dr = self.nx
                    dtheta = self.ny/5
                    dphi = self.nz/5
                    p.setPen(QPen(
                        QColor(Qt.black), self.config['size'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                    p.setBrush(QBrush(QColor(Qt.black)))

                    poslist = []
                    for i in range(0, len(self.xpos)-1, 2):
                        p.drawRect(
                            QRectF(xs[i]+300, -ys[i]+300, xs[i+1]-xs[i], -ys[i+1]+ys[i]))
                        xmax = max([self.xpos[i+1], self.xpos[i]])
                        xmin = min([self.xpos[i+1], self.xpos[i]])
                        ymax = max([self.ypos[i+1], self.ypos[i]])
                        ymin = min([self.ypos[i+1], self.ypos[i]])
                        zmax = max([self.zpos[i+1], self.zpos[i]])
                        zmin = min([self.zpos[i+1], self.zpos[i]])

                        if self.centers == '':
                            cx = (xmax+xmin)/2
                            cy = (ymax+ymin)/2
                            cz = (zmax+zmin)/2
                        else:
                            str1 = self.centers
                            str1 = np.array(str1.replace('(', '').replace(')', '').split(
                                ','), dtype=float).reshape(-1, 3)
                            xs1 = [5*x[0] for x in str1]
                            ys1 = [5*x[1] for x in str1]
                            zs1 = [5*x[2] for x in str1]
                            cx = (xs1[i] + xs1[i+1])/2
                            cy = (ys1[i] + ys1[i+1])/2
                            cz = (zs1[i] + zs1[i+1])/2
                        # NEED TO RECALCULATE POINT GENERATING PARAMETERS TO GET APPROPRIATE ONES WITHIN THE REGION.

                        r = (np.sqrt((xmax-xmin)**2 +
                             (ymax-ymin)**2 + (zmax-zmin)**2))

                        linval = math.floor(r/(dr))

                        thetavals = np.linspace(
                            0, 1, math.floor(360/dtheta) + 1)
                        phivals = np.linspace(0, 1, math.floor(180/dphi) + 1)
                        parvals = np.linspace(0, 1, linval+1)
                        positions = [[cx,cy,cz]]
                        for t in parvals[1:]:
                            for z in thetavals[1:]:
                                for p in phivals[1:]:
                                    xval = cx + t*r * \
                                        np.cos(z*2*np.pi)*np.sin(p*np.pi)
                                    yval = cy + t*r * \
                                        np.sin(z*2*np.pi)*np.sin(p*np.pi)
                                    zval = cz + t*r*np.cos(p*np.pi)
                                    if (xval > xmax) or xval < xmin or yval > ymax or yval < ymin or zval > zmax or zval < zmin:
                                        pass
                                    else:
                                        positions.append([xval, yval, zval])

                        poslist.extend(positions)

                    self.poslist = poslist
                except ValueError:
                    QMessageBox.about(
                        self, "Error", "Position should be valid numbers.")

        elif self.mode == 'circle':

            if self.grid == 'circle':
                poslist = []
                bar = self.bar

                try:

                    xs = [5*x[0] for x in str1]
                    ys = [5*x[1] for x in str1]
                    zs = [5*x[2] for x in str1]
                    self.xpos = xs
                    self.ypos = ys
                    self.zpos = zs
                    dr = self.nx
                    dtheta = self.ny/5
                    nz = self.nz
                    p.setPen(QPen(
                        QColor(Qt.black), self.config['size'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                    p.setBrush(QBrush(QColor(Qt.black)))

                    poslist = []
                    xpos = [xs[0]]
                    ypos = [ys[0]]

                    for i in range(0, len(self.xpos)-1, 2):

                        xposi = xs[i]
                        xposi2 = xs[i+1]

                        yposi = ys[i]
                        yposi2 = ys[i+1]

                        zmax = zs[i+1]
                        zmin = zs[i]
                        linvalz = abs(math.floor((zmax-zmin)/(nz)))

                        zvals = np.linspace(zmin, zmax, linvalz+1)
                        r = np.sqrt((xposi - xposi2)**2 + (yposi-yposi2)**2)

                        dr = self.nx
                        dtheta = self.ny/5

                        p.drawEllipse(QPointF(xs[i]+300, -ys[i]+300), r, r)
                        linval = math.floor(r/(dr))

                        thetavals = np.linspace(
                            0, 1, math.floor(360/dtheta) + 1)
                        parvals = np.linspace(0, 1, linval+1)

                        for t in parvals[1:]:
                            for z in thetavals[1:]:
                                xval = xposi + t*r*np.cos(z*2*np.pi)
                                yval = yposi + t*r*np.sin(z*2*np.pi)

                                xpos = np.append(xpos, xval)
                                ypos = np.append(ypos, yval)

                    for z in range(0, len(zvals)):
                        zpos = z*np.ones(len(xpos))
                        positions = list(zip(xpos, ypos, zpos))
                        poslist = poslist + positions

                    self.poslist = poslist

                except ValueError:
                    QMessageBox.about(
                        self, "Error", "Position should be valid numbers.")

            if self.grid == 'rect':
                poslist = []
                bar = self.bar

                try:

                    xs = [5*x[0] for x in str1]
                    ys = [5*x[1] for x in str1]
                    zs = [5*x[2] for x in str1]
                    self.xpos = xs
                    self.ypos = ys
                    self.zpos = zs
                    nx = self.nx
                    ny = self.ny
                    nz = self.nz
                    p.setPen(QPen(
                        QColor(Qt.black), self.config['size'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                    p.setBrush(QBrush(QColor(Qt.black)))

                    poslist = []
                    xpos = []
                    ypos = []
                    zpos = []

                    for i in range(0, len(self.xpos)-1, 2):

                        xposi = xs[i]
                        xposi2 = xs[i+1]

                        yposi = ys[i]
                        yposi2 = ys[i+1]

                        zmax = zs[i+1]
                        zmin = zs[i]

                        if self.centers == '':
                            cx = xposi
                            cy = yposi
                            cz = (zmax+zmin)/2
                        else:
                            str1 = self.centers
                            str1 = np.array(str1.replace('(', '').replace(')', '').split(
                                ','), dtype=float).reshape(-1, 3)
                            xs = [5*x[0] for x in str1]
                            ys = [5*x[1] for x in str1]
                            zs = [5*x[2] for x in str1]
                            cx = xs[i]
                            cy = ys[i]
                            cz = zs[i]

                        r = np.sqrt((xposi - xposi2)**2 + (yposi-yposi2)**2)
                        xmax = cx + r
                        xmin = cx - r
                        ymax = cy + r
                        ymin = cy - r

                        p.drawEllipse(QPointF(xs[i]+300, -ys[i]+300), r, r)

                        linvalz = abs(math.floor((zmax-zmin)/(nz)))

                        linvalx = abs(math.floor((xmax-xmin)/(nx)))
                        linvaly = abs(math.floor((ymax-ymin)/(ny)))

                        zvals = np.linspace(zmin, zmax, linvalz+1)
                        xvals = np.linspace(xmin, xmax, linvalx+1)
                        yvals = np.linspace(ymin, ymax, linvaly+1)

                        positions = []
                        for z in range(0, len(zvals)):
                            for x in range(0, len(xvals)):
                                for y in range(0, len(yvals)):
                                    if (xvals[x] - cx)**2 + (yvals[y] - cy)**2 <= r**2 and zvals[z] <= zmax and zvals[z] >= zmin:
                                        positions.append(
                                            [xvals[x], yvals[y], zvals[z]])
                                    else:
                                        pass

                    poslist.extend(positions)
                    self.poslist = poslist

                except ValueError:
                    QMessageBox.about(
                        self, "Error", "Position should be valid numbers.")

            if self.grid == 'sphere':
                poslist = []
                bar = self.bar

              
                try:

                    xs = [5*x[0] for x in str1]
                    ys = [5*x[1] for x in str1]
                    zs = [5*x[2] for x in str1]
                    self.xpos = xs
                    self.ypos = ys
                    self.zpos = zs
                    dr = self.nx
                    dtheta = self.ny/5
                    dphi = self.nz/5
                   
                    p.setPen(QPen(
                        QColor(Qt.black), self.config['size'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                    p.setBrush(QBrush(QColor(Qt.black)))

                    poslist = []
                    
                    for i in range(0, len(self.xpos)-1, 2):

                        xposi = xs[i]
                        xposi2 = xs[i+1]

                        yposi = ys[i]
                        yposi2 = ys[i+1]

                        zmax = zs[i+1]
                        zmin = zs[i]

                        if self.centers == '':
                            cx = xposi
                            cy = yposi
                            cz = (zmax+zmin)/2
                        else:
                            str1 = self.centers
                            str1 = np.array(str1.replace('(', '').replace(')', '').split(
                                ','), dtype=float).reshape(-1, 3)
                            xs = [5*x[0] for x in str1]
                            ys = [5*x[1] for x in str1]
                            zs = [5*x[2] for x in str1]
                            cx = xs[i]
                            cy = ys[i]
                            cz = zs[i]

                        rc = np.sqrt((xposi - xposi2)**2 + (yposi-yposi2)**2)
                        xmax = cx + rc
                        xmin = cx - rc
                        ymax = cy + rc
                        ymin = cy - rc

                        p.drawEllipse(QPointF(xs[i]+300, -ys[i]+300), rc, rc)

                        r = 0.5*(np.sqrt((xmax-xmin)**2 + (ymax-ymin)**2) + (zmax-zmin)**2)

                        linval = math.floor(r/(dr))

                        thetavals = np.linspace(0, 1, math.floor(360/dtheta) + 1)
                        phivals = np.linspace(0,1,math.floor(180/dphi)+1)
                        parvals = np.linspace(0, 1, linval+1)
                        positions = [[cx,cy,cz]]
                        # first start point already initialized in array.
                        for t in parvals[1:]:
                            # Other start points are incorporated as the end points of previous segment.
                            for z in thetavals[1:]:
                                for p in phivals[1:]:
                                    xval = cx + t*r*np.cos(z*2*np.pi)*np.sin(p*np.pi)
                                    yval = cy + t*r*np.sin(z*2*np.pi)*np.sin(p*np.pi)
                                    zval = cz + t*r*np.cos(p*np.pi)
                                if (xval-cx)**2 + (yval-cy)**2 > rc**2 or zval > zmax or zval < zmin:
                                    pass
                                else:
                                    positions.append([xval, yval, zval])

                        poslist = poslist + positions

                    self.poslist = poslist

                except ValueError:
                    QMessageBox.about(
                        self, "Error", "Position should be valid numbers.")
        
        
        
        
        elif self.mode == 'ellipse':
            
            if self.grid == 'ellipse':
                poslist = []
                bar = self.bar

                try:

                    xs = [5*x[0] for x in str1]
                    ys = [5*x[1] for x in str1]
                    zs = [5*x[2] for x in str1]
                    self.xpos = xs
                    self.ypos = ys
                    self.zpos = zs
                    dr = self.nx
                    dtheta = self.ny/5
                    nz = self.nz
                    p.setPen(QPen(
                        QColor(Qt.black), self.config['size'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                    p.setBrush(QBrush(QColor(Qt.black)))

                    poslist = []
                    xpos = []
                    ypos = []

                    for i in range(0, len(self.xpos)-1, 2):

                        xposi = xs[i]
                        xposi2 = xs[i+1]

                        yposi = ys[i]
                        yposi2 = ys[i+1]

                        zmax = zs[i+1]
                        zmin = zs[i]
                        linvalz = abs(math.floor((zmax-zmin)/(nz)))

                        zvals = np.linspace(zmin, zmax, linvalz+1)
                        a = np.abs(xposi2-xposi)/2
                        b = np.abs(yposi2-yposi)/2
                        # zposi = zs[i]
                        # zposi2 =zs[i+1]

                        cx = (xposi + xposi2)/2
                        cy = (yposi + yposi2)/2
                        xpos = np.append(xpos, cx)
                        ypos = np.append(ypos, cy)

                        p.drawEllipse(
                            QRect(QPoint(xposi+300, -yposi+300), QPoint(xposi2+300, -yposi2+300)))
                        linval = math.floor((min([a, b]))/(dr))

                        thetavals = np.linspace(
                            0, 1, math.floor(360/dtheta) + 1)
                        parvals = np.linspace(0, 1, linval+1)

                        for t in parvals[1:]:
                            for z in thetavals[1:]:
                                xval = cx + t*a*np.cos(z*2*np.pi)
                                yval = cy + t*b*np.sin(z*2*np.pi)

                                xpos = np.append(xpos, xval)
                                ypos = np.append(ypos, yval)

                    for z in range(0, len(zvals)):
                        zpos = z*np.ones(len(xpos))
                        positions = list(zip(xpos, ypos, zpos))
                        poslist = poslist + positions

                    self.poslist = poslist

                except ValueError:
                    QMessageBox.about(
                        self, "Error", "Position should be valid numbers.")
                    
            if self.grid == 'rect':
                poslist = []
                bar = self.bar

                try:

                    xs = [5*x[0] for x in str1]
                    ys = [5*x[1] for x in str1]
                    zs = [5*x[2] for x in str1]
                    self.xpos = xs
                    self.ypos = ys
                    self.zpos = zs
                    p.setPen(QPen(
                        QColor(Qt.black), self.config['size'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                    p.setBrush(QBrush(QColor(Qt.black)))
                    nx = self.nx
                    ny = self.ny 
                    nz = self.nz
                    poslist = []
                  

                    for i in range(0, len(self.xpos)-1, 2):

                        xmax = self.xpos[i+1]
                        xmin = self.xpos[i]
                        ymax = self.ypos[i+1]
                        ymin = self.ypos[i]
                        zmax = zs[i+1]
                        zmin = zs[i]
                        linvalz = abs(math.floor((zmax-zmin)/(nz)))

                        zvals = np.linspace(zmin, zmax, linvalz+1)


                        cx = (xposi + xposi2)/2
                        cy = (yposi + yposi2)/2

                        p.drawEllipse(
                            QRect(QPoint(xposi+300, -yposi+300), QPoint(xposi2+300, -yposi2+300)))
                       
                        nx = self.nx
                        ny = self.ny
                        nz = self.nz
                        a = np.abs(xmax - xmin)/2
                        b = np.abs(ymax-  ymin)/2
                        if self.centers == '':
                                cx = (xmax + xmin)/2
                                cy = (ymax + ymin)/2
                        else:
                                str1 = self.centers
                                str1 = np.array(str1.replace('(', '').replace(')', '').split(
                                    ','), dtype=float).reshape(-1, 3)
                                xs = [5*x[0] for x in str1]
                                ys = [5*x[1] for x in str1]
                                zs = [5*x[2] for x in str1]
                                cx = xs[i]
                                cy = ys[i]
                                cz = zs[i]

                        linvalx = abs(math.floor((xmax-xmin)/(nx)))
                        linvaly = abs(math.floor((ymax-ymin)/(ny)))
                        xpos = np.linspace(xmin, xmax, linvalx+1)
                        ypos = np.linspace(ymin, ymax, linvaly+1)
                        positions = []
                        for z in range(0, len(zvals)):
                                for x in range(0, len(xpos)):
                                    for y in range(0, len(ypos)):
                                        if (((xpos[x]-cx)/a)**2 + ((ypos[y]-cy)/b)**2 <= 1):
                                            positions.append([xpos[x], ypos[y], zvals[z]])
                                        else:
                                            pass

                        poslist.extend(positions)
                    self.poslist = poslist

                except ValueError:
                    QMessageBox.about(
                        self, "Error", "Position should be valid numbers.")
                    
            if self.grid == 'circle':
                poslist = []
                bar = self.bar

                try:

                    xs = [5*x[0] for x in str1]
                    ys = [5*x[1] for x in str1]
                    zs = [5*x[2] for x in str1]
                    self.xpos = xs
                    self.ypos = ys
                    self.zpos = zs
                    p.setPen(QPen(
                        QColor(Qt.black), self.config['size'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                    p.setBrush(QBrush(QColor(Qt.black)))
                    nx = self.nx
                    ny = self.ny 
                    nz = self.nz
                    poslist = []
                  

                    for i in range(0, len(self.xpos)-1, 2):

                        xmax = self.xpos[i+1]
                        xmin = self.xpos[i]
                        ymax = self.ypos[i+1]
                        ymin = self.ypos[i]
                        zmax = zs[i+1]
                        zmin = zs[i]
                        linvalz = abs(math.floor((zmax-zmin)/(nz)))

                        zvals = np.linspace(zmin, zmax, linvalz+1)
                        p.drawEllipse(
                            QRect(QPoint(xposi+300, -yposi+300), QPoint(xposi2+300, -yposi2+300)))
                       
                        cx = (xposi + xposi2)/2
                        cy = (yposi + yposi2)/2

                        
                        nx = self.nx
                        ny = self.ny
                        nz = self.nz
                        a = np.abs(xmax - xmin)/2
                        b = np.abs(ymax-  ymin)/2
                        r = np.sqrt((xposi2 - xposi)**2 + (yposi -yposi2)**2)*0.5

                        if self.centers == '':
                            cx = (xposi + xposi2)/2
                            cy = (yposi + yposi2)/2
                        else:
                            str1 = self.centers
                            str1 = np.array(str1.replace('(', '').replace(')', '').split(
                                ','), dtype=float).reshape(-1, 3)
                            xs = [5*x[0] for x in str1]
                            ys = [5*x[1] for x in str1]
                            zs = [5*x[2] for x in str1]
                            cx = xs[i]
                            cy = ys[i]
                            cz = zs[i]
                        xpos = [cx]
                        ypos = [cy]
                        linval = math.floor(r/dr)

                        thetavals = np.linspace(0, 1, math.floor(360/dtheta) + 1)
                        parvals = np.linspace(0, 1, linval+1)

                        for t in parvals[1:]:
                            for z in thetavals[1:]:
                                xval = cx + t*r*np.cos(z*2*np.pi)
                                yval = cy + t*r*np.sin(z*2*np.pi)
                                if ((xval-cx)/a)**2 + ((yval-cy)/b)**2 <= 1:
                                    xpos = np.append(xpos, xval)
                                    ypos = np.append(ypos, yval)

                    for z in range(0, len(zvals)):
                        zpos = z*np.ones(len(xpos))
                        positions = list(zip(xpos, ypos, zpos))
                        poslist = poslist + positions

                    self.poslist = poslist

                except ValueError:
                    QMessageBox.about(
                        self, "Error", "Position should be valid numbers.")

    def enter(self,arg, mode):
        ''' When selecting grid-style, launch pop-up window for additional config info
        '''
        if self.centers == '' or arg.ea.text() == '' or (arg.eb.text() == '' and mode == 'rect') :
            pass
        else:
            str1 = self.centers
            str1 = np.array(str1.replace('(', '').replace(')', '').split(','), dtype=float).reshape(-1, 3)
            xs1 = [x[0] for x in str1]
            ys1 = [x[1] for x in str1]
            zs1 = [x[2] for x in str1]
            z1 = self.z1/5
            z2 = self.z2/5
                
            eb = str(arg.eb.text())
            ea = str(arg.ea.text())

            ea = [int(s) for s in ea.split(',')]
            if eb != '':
                eb = [int(s) for s in eb.split(',')]            
            str1 = ''
           
            if mode == 'circle':
                dr = self.nx/5
                dtheta = self.ny/5
                dz = self.nz/5

                for i in range(0,len(xs1)):
                    perRing = 360/dtheta
                    ringnum = math.floor(ea[i]/perRing)
                    r = ringnum*dr
                    str0 = '(' + str(xs1[i])+','+str(ys1[i])+','+str(z1)+'), ('+str(xs1[i]+r)+','+str(ys1[i])+','+str(z2)+')'
                    str1 = str1 + str0
                
                self.str1 = str1
                self.coordEnter(arg, str1)
            
            if mode == 'rect':
                
                dx = self.nx/5
                dy = self.ny/5

                for i in range(0,len(xs1)):
                    
                    rx = (ea[i]-1)*dx/2
                    ry = (eb[i]-1)*dy/2
                    str0 = '('+ str(rx + xs1[i])+','+str(ry+ys1[i])+','+str(z1)+'), ('+str(xs1[i]-rx)+','+str(ys1[i]-ry)+','+str(z2)+')'
                    str1 = str1 + str0
                
                self.str1 = str1
                self.coordEnter(arg, str1)
                
            # else:
            #     raise ValueError("AAAAAAAAAAAA")
                
            if mode == 'ellipse':
                dr = self.nx/5
                dtheta = self.ny/5
                dz = self.nz/5
                e = self.eccentricity
                for i in range(0,len(xs1)):
                    perRing = 360/dtheta
                    a = (ea[i]/perRing)*(dr/(1-e**2)**0.5)
                    b = (ea[i]/perRing)*dr
                    str0 = '('+ str(a + xs1[i])+','+str(b+ys1[i])+','+str(z1)+'), ('+str(xs1[i]-a)+','+str(ys1[i]-b)+','+str(z2)+')'
                    str1 = str1 + str0
                
                self.str1 = str1
                self.coordEnter(arg, str1)
                
            if mode == 'sphere':
                pass
            
    def save_file(self):

        with open("file.txt", 'w') as file:
            for row in self.poslist:
                s = " ".join(map(str, row))
                file.write(s+'\n')

        with open("res.txt", 'w') as file:
            file.write(str(self.nx/5) + ' ' +
                       str(self.ny/5)+' ' + str(self.nz/5))

        Dict = {'mode': self.mode, 'xres': self.nx, 'yres': self.ny, 'zres': self.nz,
                'xs': self.xpos, 'ys': self.ypos, 'zs': self.zpos, 'bar': self.barlist, hand: self.hand, close: self.closeit}
        toml_string = toml.dumps(Dict)  # Output to a string

        output_file_name = "output.toml"
        with open(output_file_name, "w") as toml_file:
            toml.dump(Dict, toml_file)


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, *args, **kwargs):
        '''connect UI to functions'''
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.mode = 'rect'
        self.checkBoxlabel = None
        self.ecc = None
        self.eccentricity = 0.5
        self.closeit = None
        self.canvas = Canvas()
        self.canvas.initialize()
        self.canvas.setFixedHeight(600)
        self.canvas.setFixedWidth(600)
        # We need to enable mouse tracking to follow the mouse without the button pressed.
        self.canvas.setMouseTracking(True)
        # # Enable focus to capture key inputs.
        # self.canvas.setFocusPolicy(Qt.StrongFocus)
        self.horizontalLayout.addWidget(self.canvas)
        
        self.canvas2 = MplCanvas()
        self.horizontalLayout.addWidget(self.canvas2)
       
        #Connect mode Box
        self.modeBox.currentIndexChanged.connect(lambda: [self.get_index(), self.canvas.set_mode(self.mode),  self.btnstate2(self.generateBox, n = 1)])

        # Setup Grid Box
        self.gridBox.currentIndexChanged.connect(lambda: [self.get_index2(), self.canvas.set_grid(self.grid)])

        #Connect IPBox:
        self.AxesBox.currentIndexChanged.connect(lambda: self.IPBoxsetter())
        
        self.printButton.clicked.connect(lambda: [self.canvas.print_positions(self), self.update_graph(
            self.canvas.poslist, self.canvas.nx, self.canvas.ny, self.canvas.barlist, self.canvas.mode)])
        self.clearButton.clicked.connect(lambda: [self.canvas.reset(), self.canvas.resetpos(self), self.update_graph(
            self.canvas.poslist, self.canvas.nx, self.canvas.ny, self.canvas.barlist, self.canvas.mode)])
        self.saveButton.clicked.connect(lambda: self.canvas.save_file())
        self.verifyButton.clicked.connect(lambda: self.canvas.checklist(self))
        self.EntButton.clicked.connect(lambda: [self.canvas.reset(), self.canvas.resetpos(self), self.canvas.coordEnter(
            self), self.update_graph(self.canvas.poslist, self.canvas.nx, self.canvas.ny, self.canvas.barlist, self.canvas.mode)])
        # self.hand.clicked.connect(
        #     lambda: [self.canvas.set_hand(), self.canvas.resetpos(self)])

        # Initialize animation timer.
        self.timer = QTimer()
        self.timer.timeout.connect(self.canvas.on_timer)
        self.timer.setInterval(100)
        self.timer.start()

        self.xres.editingFinished.connect(lambda: self.canvas.set_status(self))
        self.yres.editingFinished.connect(lambda: self.canvas.set_status(self))
        self.zres.editingFinished.connect(lambda: self.canvas.set_status(self))
        self.gridCentre.editingFinished.connect(lambda: self.canvas.set_status(self))
        self.z1.editingFinished.connect(lambda: self.canvas.set_status(self))
        self.z2.editingFinished.connect(lambda: self.canvas.set_status(self))
        self.canvas.move.connect(lambda: self.updateCoord(
            self.canvas.cx, self.canvas.cy, self.canvas.poslist, self.canvas.bar))
        self.hand.clicked.connect(lambda: [self.canvas.set_hand() ,self.canvas.resetpos(self)])
        self.generateBox.stateChanged.connect(lambda: self.btnstate2(self.generateBox))





        sizeicon = QLabel()
        sizeicon.setPixmap(
            QPixmap(os.path.join('images', 'border-weight.png')))

        self.show()

    def update_graph(self, poslist, nx, ny, barlist, arg):
        ''' ROutine to update Matplotlib graph displaying actual data points defined so far, 
        as well as barriers and no-go zones'''
        self.horizontalLayout.removeWidget(self.canvas2)

        self.canvas2 = MplCanvas()
        self.canvas2.ax.set_xlim3d(-100, 100)
        self.canvas2.ax.set_ylim3d(-100, 100)
        self.canvas2.ax.set_zlim3d(-5, 5)

        xs = [x[0]/5 for x in poslist]
        ys = [x[1]/5 for x in poslist]
        zs = [x[2]/5 for x in poslist]
        if arg == 'circle':
            size = nx/10
        else:
            size = min([nx/5, ny/5])

        self.canvas2.ax.scatter(xs, ys, zs, s=size)

        for posgroup in barlist:
            #posgroup is [(xorg,y,z),(xe),(xvo),(xve)]

            self.canvas2.ax.plot([posgroup[0][0], posgroup[1][0]],
                                 [posgroup[0][1], posgroup[1][1]], color='#800000'
                                 )
            self.canvas2.ax.plot([posgroup[0][0], posgroup[2][0]],
                                 [posgroup[0][1], posgroup[2][1]], color='red'
                                 )
            self.canvas2.ax.plot([posgroup[1][0], posgroup[3][0]],
                                 [posgroup[1][1], posgroup[3][1]], color='red'
                                 )
        self.horizontalLayout.addWidget(self.canvas2)

    def updateCoord(self, x, y, poslist, bar):
        '''Display current cursor coordinates in LAPD, cm units'''
        self.coordLabel.setText(
            'Mouse coords: ( %d , %d )' % ((x-300)/5, (-y+300)/5))
        self.pointnumberLabel2.setText(str(len(poslist)))


  

    def get_index(self):
        index = self.modeBox.currentIndex()
        if index == None:
            pass
        if index == 5:
            self.mode = 'barrier'
            if self.checkBoxlabel:
                self.vl.removeWidget(self.checkBoxlabel)
                self.vl.removeWidget(self.checkBox)
                self.checkBox.deleteLater()
                self.checkBox = None
                self.checkBoxlabel.deleteLater()
                self.checkBoxlabel = None

        elif index == 0:
            self.mode = 'rect'
            if self.checkBoxlabel:
                self.vl.removeWidget(self.checkBoxlabel)
                self.vl.removeWidget(self.checkBox)
                self.checkBox.deleteLater()
                self.checkBox = None
                self.checkBoxlabel.deleteLater()
                self.checkBoxlabel = None

        elif index == 1:
            self.mode = 'circle'
            if self.checkBoxlabel:
                self.vl.removeWidget(self.checkBoxlabel)
                self.vl.removeWidget(self.checkBox)
                self.checkBox.deleteLater()
                self.checkBox = None
                self.checkBoxlabel.deleteLater()
                self.checkBoxlabel = None

        elif index == 2:
            self.mode = 'line'
            if self.checkBoxlabel:
                self.vl.removeWidget(self.checkBoxlabel)
                self.vl.removeWidget(self.checkBox)
                self.checkBox.deleteLater()
                self.checkBox = None
                self.checkBoxlabel.deleteLater()
                self.checkBoxlabel = None

        elif index == 3:
            self.mode = 'polyline'
            self.checkBoxlabel = QtWidgets.QLabel(self.groupBox)
            self.checkBoxlabel.setMaximumWidth(150)
            self.vl.addWidget(self.checkBoxlabel)
            self.checkBoxlabel.setText( "Auto-close polygon?")
            self.checkBox = QtWidgets.QCheckBox(self.groupBox)
            self.checkBox.setObjectName("checkBox")
            self.checkBox.setMaximumWidth(150)
            self.vl.addWidget(self.checkBox)
            self.checkBox.stateChanged.connect(lambda: self.btnstate(self.checkBox))
    
        elif index == 4: 
            self.mode = 'ellipse'
            if self.checkBoxlabel:
                self.vl.removeWidget(self.checkBoxlabel)
                self.vl.removeWidget(self.checkBox)
                self.checkBox.deleteLater()
                self.checkBox = None
                self.checkBoxlabel.deleteLater()
                self.checkBoxlabel = None

    def get_index2(self):
        index = self.gridBox.currentIndex()
        
        if index == None:
            pass
        if index ==0:
            self.grid = 'rect'
            self.xreslabel.setText( "dx (cm)")
            self.yreslabel.setText( "dy (cm)")
            self.zreslabel.setText("dz (cm)")
            if self.ecc:
                self.verticalLayout_2.removeWidget(self.ecc)
                self.ecc.deleteLater()
                self.ecc = None
        elif index == 1:
            self.grid = 'circle'
            self.xreslabel.setText( "dr (cm)")
            self.yreslabel.setText( "dθ (degrees)")
            self.zreslabel.setText("dz (cm)")
            if self.ecc:
                self.verticalLayout_2.removeWidget(self.ecc)
                self.ecc.deleteLater()
                self.ecc = None
        elif index ==3 :
            self.grid = 'ellipse'
            self.xreslabel.setText( "dr (cm)")
            self.yreslabel.setText( "dθ (degrees)")
            self.zreslabel.setText("dz (cm)")
            #############TO BE IMPLEMENTED
            self.ecc = QtWidgets.QLineEdit(self.groupBox)
            self.ecc.setMaximumWidth(150)
            self.ecc.setObjectName("ecc")
            self.ecc.setText("Enter eccentricity of ellipse")
            self.verticalLayout_2.addWidget(self.ecc)
            self.ecc.editingFinished.connect(lambda: self.getecc() )
            
            
        elif index ==2 :
            self.grid = 'sphere'
            self.xreslabel.setText( "dr (cm)")
            self.yreslabel.setText( "dθ (degrees)")
            self.zreslabel.setText("dφ (degrees)")
            if self.ecc:
                self.verticalLayout_2.removeWidget(self.ecc)
                self.ecc.deleteLater()
                self.ecc = None
    
    def getecc(self): ########TO BE IMPLEMENTED
        try:
            self.eccentricity = float(self.ecc.text())
            self.canvas.set_status(self)
        except ValueError:
            QMessageBox.about(
            self, "Error", "Eccentricity should be valid numbers.")
    def btnstate(self,b):
        if b.isChecked() == True:
            self.closeit = True
        else:
            self.closeit = False
        self.canvas.set_status(self)
        
    def btnstate2(self,b,n = 0):
        if b.isChecked() == True:
            self.gridBox.setEnabled(False)

            if n == 1:
                    self.gridV.removeWidget(self.ea)
                    self.ea.deleteLater()
                    self.ea = None
                    
                    self.gridV.removeWidget(self.eb)
                    self.eb.deleteLater()
                    self.eb = None
                    
            if self.mode == 'rect':
                self.gridBox.setCurrentIndex(0)
                self.canvas.set_grid('rect')
                self.canvas.mode = 'rect'
                self.ea = QtWidgets.QLineEdit(self.groupBox)
                self.ea.setMaximumWidth(150)
                self.ea.setObjectName("ea")
                self.ea.setText("No. of points: X")
                self.gridV.addWidget(self.ea)
                self.ea.editingFinished.connect(lambda: [self.canvas.reset(), self.canvas.resetpos(self), self.canvas.enter(self,self.mode), self.update_graph(self.canvas.poslist, self.canvas.nx, self.canvas.ny, self.canvas.barlist, self.canvas.mode)])
                
                self.eb = QtWidgets.QLineEdit(self.groupBox)
                self.eb.setMaximumWidth(150)
                self.eb.setObjectName("eb")
                self.eb.setText("No. of points: Y")
                self.gridV.addWidget(self.eb)
                self.eb.editingFinished.connect(lambda:  [self.canvas.reset(), self.canvas.resetpos(self), self.canvas.enter(self,self.mode), self.update_graph(self.canvas.poslist, self.canvas.nx, self.canvas.ny, self.canvas.barlist, self.canvas.mode)])
 
                self.gridCentre.editingFinished.connect(lambda: [self.canvas.set_status(self),self.canvas.reset(), self.canvas.resetpos(self), self.canvas.enter(self,self.mode), self.update_graph(self.canvas.poslist, self.canvas.nx, self.canvas.ny, self.canvas.barlist, self.canvas.mode)] )
                self.xres.editingFinished.connect(lambda: [self.canvas.set_status(self),self.canvas.reset(), self.canvas.resetpos(self), self.canvas.enter(self,self.mode), self.update_graph(self.canvas.poslist, self.canvas.nx, self.canvas.ny, self.canvas.barlist, self.canvas.mode)] )
                self.yres.editingFinished.connect(lambda: [self.canvas.set_status(self),self.canvas.reset(), self.canvas.resetpos(self), self.canvas.enter(self,self.mode), self.update_graph(self.canvas.poslist, self.canvas.nx, self.canvas.ny, self.canvas.barlist, self.canvas.mode)] )
                self.zres.editingFinished.connect(lambda: [self.canvas.set_status(self),self.canvas.reset(), self.canvas.resetpos(self), self.canvas.enter(self,self.mode), self.update_graph(self.canvas.poslist, self.canvas.nx, self.canvas.ny, self.canvas.barlist, self.canvas.mode)] )


                
            elif self.mode == 'circle':
                self.gridBox.setCurrentIndex(1)
                self.canvas.set_grid('circle')
                self.canvas.mode = 'circle'

                self.ea = QtWidgets.QLineEdit(self.groupBox)
                self.ea.setMaximumWidth(150)
                self.ea.setObjectName("ea")
                self.ea.setText("No. of points")
                self.gridV.addWidget(self.ea)
                self.ea.editingFinished.connect(lambda:  [self.canvas.reset(), self.canvas.resetpos(self), self.canvas.enter(self,self.mode), self.update_graph(self.canvas.poslist, self.canvas.nx, self.canvas.ny, self.canvas.barlist, self.canvas.mode)])
                
                self.eb = QtWidgets.QLineEdit(self.groupBox)
                self.eb.setMaximumWidth(0)
                self.eb.setObjectName("eb")
                self.eb.setText("")
                self.gridV.addWidget(self.eb)
                self.eb.editingFinished.connect(lambda:  [self.canvas.reset(), self.canvas.resetpos(self), self.canvas.enter(self,self.mode), self.update_graph(self.canvas.poslist, self.canvas.nx, self.canvas.ny, self.canvas.barlist, self.canvas.mode)])
                
                self.gridCentre.editingFinished.connect(lambda: [self.canvas.set_status(self),self.canvas.reset(), self.canvas.resetpos(self), self.canvas.enter(self,self.mode), self.update_graph(self.canvas.poslist, self.canvas.nx, self.canvas.ny, self.canvas.barlist, self.canvas.mode)] )
                self.xres.editingFinished.connect(lambda: [self.canvas.set_status(self),self.canvas.reset(), self.canvas.resetpos(self), self.canvas.enter(self,self.mode), self.update_graph(self.canvas.poslist, self.canvas.nx, self.canvas.ny, self.canvas.barlist, self.canvas.mode)] )
                self.yres.editingFinished.connect(lambda: [self.canvas.set_status(self),self.canvas.reset(), self.canvas.resetpos(self), self.canvas.enter(self,self.mode), self.update_graph(self.canvas.poslist, self.canvas.nx, self.canvas.ny, self.canvas.barlist, self.canvas.mode)] )
                self.zres.editingFinished.connect(lambda: [self.canvas.set_status(self),self.canvas.reset(), self.canvas.resetpos(self), self.canvas.enter(self,self.mode), self.update_graph(self.canvas.poslist, self.canvas.nx, self.canvas.ny, self.canvas.barlist, self.canvas.mode)] )


            elif self.mode == 'ellipse':
                self.gridBox.setCurrentIndex(3)
                self.canvas.set_grid('ellipse')
                self.canvas.mode = 'ellipse'

                self.ea = QtWidgets.QLineEdit(self.groupBox)
                self.ea.setMaximumWidth(150)
                self.ea.setObjectName("ea")
                self.ea.setText("No. of points")
                self.gridV.addWidget(self.ea)
                self.ea.editingFinished.connect(lambda:  [self.canvas.reset(), self.canvas.resetpos(self), self.canvas.enter(self,self.mode), self.update_graph(self.canvas.poslist, self.canvas.nx, self.canvas.ny, self.canvas.barlist, self.canvas.mode)])
                
                self.eb = QtWidgets.QLineEdit(self.groupBox)
                self.eb.setMaximumWidth(0)
                self.eb.setObjectName("eb")
                self.eb.setText("")
                self.gridV.addWidget(self.eb)
                self.eb.editingFinished.connect(lambda:  [self.canvas.reset(), self.canvas.resetpos(self), self.canvas.enter(self,self.mode), self.update_graph(self.canvas.poslist, self.canvas.nx, self.canvas.ny, self.canvas.barlist, self.canvas.mode)])
               
                self.gridCentre.editingFinished.connect(lambda: [self.canvas.set_status(self),self.canvas.reset(), self.canvas.resetpos(self), self.canvas.enter(self,self.mode), self.update_graph(self.canvas.poslist, self.canvas.nx, self.canvas.ny, self.canvas.barlist, self.canvas.mode)] )
                self.xres.editingFinished.connect(lambda: [self.canvas.set_status(self),self.canvas.reset(), self.canvas.resetpos(self), self.canvas.enter(self,self.mode), self.update_graph(self.canvas.poslist, self.canvas.nx, self.canvas.ny, self.canvas.barlist, self.canvas.mode)] )
                self.yres.editingFinished.connect(lambda: [self.canvas.set_status(self),self.canvas.reset(), self.canvas.resetpos(self), self.canvas.enter(self,self.mode), self.update_graph(self.canvas.poslist, self.canvas.nx, self.canvas.ny, self.canvas.barlist, self.canvas.mode)] )
                self.zres.editingFinished.connect(lambda: [self.canvas.set_status(self),self.canvas.reset(), self.canvas.resetpos(self), self.canvas.enter(self,self.mode), self.update_graph(self.canvas.poslist, self.canvas.nx, self.canvas.ny, self.canvas.barlist, self.canvas.mode)] )


        
        else:
            self.gridBox.setEnabled(True)
            if n == 0:
                self.gridV.removeWidget(self.ea)
                self.ea.deleteLater()
                self.ea = None
                
                self.gridV.removeWidget(self.eb)
                self.eb.deleteLater()
                self.eb = None
 
    def IPBoxsetter(self):
        index = self.AxesBox.currentIndex()
        if index == None:
            pass
        if index ==0:
           
            self.ipz.setEnabled(False)
            self.ymotorLabel.setText("Y-motor")

            
        if index ==1:
            self.ipz.setEnabled(True)
            self.ymotorLabel.setText("Y-motor")

            
        if index ==2:
            self.ipz.setEnabled(False)
            self.ymotorLabel.setText("ϴ-motor")
#################################################################################


if __name__ == '__main__':

    app = QApplication([])
    app.setQuitOnLastWindowClosed(True)
    window = MainWindow()
    app.exec_()
