# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'paint.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from qtwidgets import AnimatedToggle


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        # MainWindow.resize(1000, 800)
        self.showMaximized()      
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        # self.tabWidget.setExpanding(True)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 1300, 2200))
        self.tabWidget.setObjectName("tabWidget")
        
        
        ##################### Probe Drive stuff
        self.PD = QtWidgets.QWidget()
        self.PD.setObjectName("PD")
        self.label_12 = QtWidgets.QLabel(self.PD)
        self.label_12.setGeometry(QtCore.QRect(30, 30, 131, 21))
        self.label_12.setObjectName("label_12")
        self.comboBox_3 = QtWidgets.QComboBox(self.PD)
        self.comboBox_3.setGeometry(QtCore.QRect(30, 70, 101, 22))
        self.comboBox_3.setObjectName("comboBox_3")
        self.line = QtWidgets.QFrame(self.PD)
        self.line.setGeometry(QtCore.QRect(173, 30, 20, 491))
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.label_13 = QtWidgets.QLabel(self.PD)
        self.label_13.setGeometry(QtCore.QRect(190, 30, 181, 20))
        self.label_13.setObjectName("label_13")
        self.lineEdit_9 = QtWidgets.QLineEdit(self.PD)
        self.lineEdit_9.setGeometry(QtCore.QRect(190, 70, 113, 20))
        self.lineEdit_9.setObjectName("lineEdit_9")
        self.AxesBox = QtWidgets.QComboBox(self.PD)
        self.AxesBox.setGeometry(QtCore.QRect(190, 120, 69, 22))
        self.AxesBox.setObjectName("AxesBox")
        self.AxesBox.addItem("")
        self.AxesBox.addItem("")
        self.AxesBox.addItem("")
        self.label_14 = QtWidgets.QLabel(self.PD)
        self.label_14.setGeometry(QtCore.QRect(190, 100, 121, 16))
        self.label_14.setObjectName("label_14")
        self.label_15 = QtWidgets.QLabel(self.PD)
        self.label_15.setGeometry(QtCore.QRect(190, 150, 211, 20))
        self.label_15.setObjectName("label_15")
       
        self.IPBox = QtWidgets.QGroupBox(self.PD)
        self.IPBox.setGeometry(QtCore.QRect(190, 180, 301, 110))
        self.IPBox.setObjectName("IPBox")
        self.ipx = QtWidgets.QLineEdit(self.IPBox)
        self.ipx.setGeometry(QtCore.QRect(120, 20, 113, 20))
        self.ipx.setObjectName("ipx")
        self.xmotorLabel = QtWidgets.QLabel(self.IPBox)
        self.xmotorLabel.setGeometry(QtCore.QRect(20, 20, 47, 13))
        self.xmotorLabel.setObjectName("xmotorLabel")
        self.ymotorLabel = QtWidgets.QLabel(self.IPBox)
        self.ymotorLabel.setGeometry(QtCore.QRect(20, 50, 47, 13))
        self.ymotorLabel.setObjectName("ymotorLabel")
        self.ipy = QtWidgets.QLineEdit(self.IPBox)
        self.ipy.setGeometry(QtCore.QRect(120, 50, 113, 20))
        self.ipy.setObjectName("ipy")
        
        self.zmotorLabel = QtWidgets.QLabel(self.IPBox)
        self.zmotorLabel.setGeometry(QtCore.QRect(20, 80, 47, 13))
        self.zmotorLabel.setObjectName("zmotorLabel")
        
        self.ipz = QtWidgets.QLineEdit(self.IPBox)
        self.ipz.setGeometry(QtCore.QRect(120, 80, 113, 20))
        self.ipz.setObjectName("ipz")
        self.ipz.setEnabled(False)

        self.label_18 = QtWidgets.QLabel(self.PD)
        self.label_18.setGeometry(QtCore.QRect(190, 300, 171, 20))
        self.label_18.setObjectName("label_18")
        self.label_19 = QtWidgets.QLabel(self.PD)
        self.label_19.setGeometry(QtCore.QRect(190, 350, 161, 16))
        self.label_19.setObjectName("label_19")
        self.label_20 = QtWidgets.QLabel(self.PD)
        self.label_20.setGeometry(QtCore.QRect(190, 400, 121, 16))
        self.label_20.setObjectName("label_20")
        self.lineEdit_12 = QtWidgets.QLineEdit(self.PD)
        self.lineEdit_12.setGeometry(QtCore.QRect(190, 320, 113, 20))
        self.lineEdit_12.setObjectName("lineEdit_12")
        self.lineEdit_13 = QtWidgets.QLineEdit(self.PD)
        self.lineEdit_13.setGeometry(QtCore.QRect(190, 370, 113, 20))
        self.lineEdit_13.setObjectName("lineEdit_13")
        self.comboBox_5 = QtWidgets.QComboBox(self.PD)
        self.comboBox_5.setGeometry(QtCore.QRect(190, 420, 81, 22))
        self.comboBox_5.setObjectName("comboBox_5")
        self.label_21 = QtWidgets.QLabel(self.PD)
        self.label_21.setGeometry(QtCore.QRect(190, 450, 151, 16))
        self.label_21.setObjectName("label_21")
        self.lineEdit_14 = QtWidgets.QLineEdit(self.PD)
        self.lineEdit_14.setGeometry(QtCore.QRect(190, 470, 113, 20))
        self.lineEdit_14.setObjectName("lineEdit_14")
        self.label_22 = QtWidgets.QLabel(self.PD)
        self.label_22.setGeometry(QtCore.QRect(190, 510, 131, 16))
        self.label_22.setObjectName("label_22")
        self.tabWidget.addTab(self.PD, "")
        ############################ Probe config stuff
        
        
        self.PC = QtWidgets.QWidget()
        self.PC.setObjectName("PC")
        
        self.comboBox_6 = QtWidgets.QComboBox(self.PC)
        self.comboBox_6.setGeometry(QtCore.QRect(50, 70, 69, 22))
        self.comboBox_6.setObjectName("comboBox_6")
        self.label_23 = QtWidgets.QLabel(self.PC)
        self.label_23.setGeometry(QtCore.QRect(50, 40, 121, 16))
        self.label_23.setObjectName("label_23")
        self.line_2 = QtWidgets.QFrame(self.PC)
        self.line_2.setGeometry(QtCore.QRect(143, 40, 20, 481))
        self.line_2.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.label_24 = QtWidgets.QLabel(self.PC)
        self.label_24.setGeometry(QtCore.QRect(170, 40, 201, 16))
        self.label_24.setObjectName("label_24")
        self.tabWidget.addTab(self.PC, "")
        
        ############## MOTION LIST STUFF
        self.ML = QtWidgets.QWidget()
        self.ML.setObjectName("ML")
        
        self.widget = QtWidgets.QWidget(self.ML)
        self.widget.setGeometry(QtCore.QRect(0, 0, 1240, 650))
        self.widget.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                                 QtWidgets.QSizePolicy.Expanding))
        self.widget.setObjectName("widget")
        
        #overall layout
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setContentsMargins(2, 0, 2, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        
        #layout with canvases and mode stuff
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        
        self.groupBox = QtWidgets.QGroupBox(self.widget)
        self.groupBox.setObjectName("groupBox")
        self.groupBox.setGeometry(QtCore.QRect(10, 20, 160, 160))

        
        #groupBox mode stuff
        self.widget1 = QtWidgets.QWidget(self.groupBox)
        self.widget1.setGeometry(QtCore.QRect(10, 20, 160, 160))
        self.widget1.setObjectName("widget1")
        
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setContentsMargins(2, 0, 2, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        #label = choose mode label
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setMaximumSize(QtCore.QSize(150, 20))
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        
        #Mode style box
        
        self.vl = QtWidgets.QVBoxLayout(self.groupBox)
        
        self.modeBox = QtWidgets.QComboBox(self.groupBox)
        self.modeBox.setObjectName("modeBox")
        self.modeBox.addItem("")
        self.modeBox.addItem("")
        self.modeBox.addItem("")
        self.modeBox.addItem("")
        self.modeBox.addItem("")
        self.modeBox.addItem("")
        self.modeBox.setMaximumWidth(150)
        self.modeBox.SelectedIndex = 0
        self.vl.addWidget(self.modeBox)
        self.verticalLayout_2.addLayout(self.vl)
        
        #label_7 - choose grid style
        self.label_7 = QtWidgets.QLabel(self.groupBox)
        self.label_7.setMaximumSize(QtCore.QSize(150, 20))
        self.label_7.setObjectName("label_7")
        self.verticalLayout_2.addWidget(self.label_7)
        
        #grid box stuff
        
        self.gridBox = QtWidgets.QComboBox(self.groupBox)
        self.gridBox.setObjectName("gridBox")
        self.gridBox.addItem("")
        self.gridBox.addItem("")
        self.gridBox.addItem("")
        self.gridBox.addItem("")
        self.gridBox.setMaximumWidth(150)
        self.verticalLayout_2.addWidget(self.gridBox)
        
        self.gridV = QtWidgets.QVBoxLayout(self.groupBox)
        self.gridL = QtWidgets.QHBoxLayout(self.groupBox)

        self.generatorlabel = QtWidgets.QLabel(self.groupBox)
        self.generatorlabel.setMaximumWidth(150)
        self.gridL.addWidget(self.generatorlabel)
        
        self.generateBox = QtWidgets.QCheckBox(self.groupBox)
        self.generateBox.setObjectName("generateBox")
        self.generateBox.setMaximumWidth(150)
        self.gridL.addWidget(self.generateBox)
        self.gridV.addLayout(self.gridL)
        
        self.verticalLayout_2.addLayout(self.gridV)
        
        
        self.gridCentreLabel = QtWidgets.QLabel(self.groupBox)
        self.gridCentreLabel.setMaximumSize(QtCore.QSize(150, 20))
        self.gridCentreLabel.setObjectName("gridCentreLabel")
        self.verticalLayout_2.addWidget(self.gridCentreLabel)
        
        self.gridCentre = QtWidgets.QLineEdit(self.groupBox)
        self.gridCentre.setObjectName("gridCentre")
        self.gridCentre.setMaximumWidth(150)
        self.verticalLayout_2.addWidget(self.gridCentre)
        

        self.gridResLabel = QtWidgets.QLabel(self.groupBox)
        self.gridResLabel.setMaximumSize(QtCore.QSize(150, 40))
        self.gridResLabel.setObjectName("gridResLabel")
        self.verticalLayout_2.addWidget(self.gridResLabel)
        
        self.hl = QtWidgets.QHBoxLayout(self.groupBox)
        self.xreslabel = QtWidgets.QLabel(self.groupBox)
        self.xreslabel.setMaximumSize(QtCore.QSize(150, 40))
        self.xreslabel.setObjectName("gridResLabel")
        self.hl.addWidget(self.xreslabel)
        
        self.xres = QtWidgets.QLineEdit(self.groupBox)
        self.xres.setObjectName("xres")
        self.xres.setMaximumWidth(150)
        self.xres.setValidator(QDoubleValidator())
        self.hl.addWidget(self.xres)
        
        self.hl2 = QtWidgets.QHBoxLayout(self.groupBox)
        self.yreslabel = QtWidgets.QLabel(self.groupBox)
        self.yreslabel.setMaximumSize(QtCore.QSize(150, 40))
        self.yreslabel.setObjectName("gridResLabel")
        self.hl2.addWidget(self.yreslabel)
        
        self.yres = QtWidgets.QLineEdit(self.groupBox)
        self.yres.setObjectName("yres")
        self.yres.setMaximumWidth(150)
        self.yres.setValidator(QDoubleValidator())
        self.hl2.addWidget(self.yres)
        
        
        self.hl3 = QtWidgets.QHBoxLayout(self.groupBox)
        self.zreslabel = QtWidgets.QLabel(self.groupBox)
        self.zreslabel.setMaximumSize(QtCore.QSize(150, 40))
        self.zreslabel.setObjectName("gridResLabel")
        self.hl3.addWidget(self.zreslabel)
        
        self.zres = QtWidgets.QLineEdit(self.groupBox)
        self.zres.setObjectName("xres")
        self.zres.setMaximumWidth(150)
        self.zres.setValidator(QDoubleValidator())
        self.hl3.addWidget(self.zres)
        
        self.verticalLayout_2.addLayout(self.hl)
        self.verticalLayout_2.addLayout(self.hl2)
        self.verticalLayout_2.addLayout(self.hl3)


        self.zrangelabel = QtWidgets.QLabel(self.groupBox)
        self.zrangelabel.setMaximumSize(QtCore.QSize(150, 20))
        self.zrangelabel.setObjectName("zrangelabel")
        self.verticalLayout_2.addWidget(self.zrangelabel)
        
        self.z1 = QtWidgets.QLineEdit(self.groupBox)
        self.z1.setObjectName("z1")
        self.z1.setMaximumWidth(150)
        self.z1.setValidator(QDoubleValidator())

        self.verticalLayout_2.addWidget(self.z1)
        self.label_11 = QtWidgets.QLabel(self.groupBox)
        self.label_11.setMaximumSize(QtCore.QSize(150, 20))
        self.label_11.setObjectName("label_11")
        self.verticalLayout_2.addWidget(self.label_11)
        self.z2 = QtWidgets.QLineEdit(self.groupBox)
        self.z2.setMaximumWidth(150)
        self.z2.setObjectName("z2")
        self.z2.setValidator(QDoubleValidator())
        self.verticalLayout_2.addWidget(self.z2)
        
        
        self.handlabel = QtWidgets.QLabel(self.groupBox)
        self.handlabel.setObjectName("handlabel")
        self.handlabel.setMaximumSize(QtCore.QSize(150, 20))
        self.verticalLayout_2.addWidget(self.handlabel)

        self.hand = AnimatedToggle(
            checked_color="#FFB000",
            pulse_checked_color="#44FFB000"
        )
        
        self.hand.setObjectName("handButton")
        self.verticalLayout_2.addWidget(self.hand)
        
        self.printButton = QtWidgets.QPushButton(self.groupBox)
        self.printButton.setObjectName("printButton")
        self.printButton.setMaximumWidth(150)

        self.verticalLayout_2.addWidget(self.printButton)
        self.clearButton = QtWidgets.QPushButton(self.groupBox)
        self.clearButton.setObjectName("clearButton")
        self.clearButton.setMaximumWidth(150)
        self.verticalLayout_2.addWidget(self.clearButton)
        self.verifyButton = QtWidgets.QPushButton(self.groupBox)
        self.verifyButton.setObjectName("verifyButton")
        self.verifyButton.setMaximumWidth(150)
        self.verticalLayout_2.addWidget(self.verifyButton)
        self.saveButton = QtWidgets.QPushButton(self.groupBox)
        self.saveButton.setObjectName("saveButton")
        self.saveButton.setMaximumWidth(150)
        self.verticalLayout_2.addWidget(self.saveButton)
        
        self.horizontalLayout.addWidget(self.groupBox)
        
        
        # self.graphicsView_2 = QtWidgets.QGraphicsView(self.widget)
        # self.graphicsView_2.setMouseTracking(True)
        # self.graphicsView_2.setObjectName("graphicsView_2")
        # self.horizontalLayout.addWidget(self.graphicsView_2)
        
        # self.graphicsView = QtWidgets.QGraphicsView(self.widget)
        # self.graphicsView.setObjectName("graphicsView")
        # self.horizontalLayout.addWidget(self.graphicsView)
        
        
        
        self.verticalLayout.addLayout(self.horizontalLayout)
        
        self.groupBox_2 = QtWidgets.QGroupBox(self.widget)
        self.groupBox_2.setMinimumSize(QtCore.QSize(0, 50))
        self.groupBox_2.setObjectName("groupBox_2")
       
        
       #coordinate entering + other info stuff.
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.cursorLabel = QtWidgets.QLabel(self.groupBox_2)
        self.cursorLabel.setObjectName("cursorLabel")
        self.horizontalLayout_2.addWidget(self.cursorLabel)
        
        self.coordLabel = QtWidgets.QLabel(self.groupBox_2)
        self.coordLabel.setObjectName("coordLabel")
        self.horizontalLayout_2.addWidget(self.coordLabel)
        
        self.pointnumberLabel = QtWidgets.QLabel(self.groupBox_2)
        self.pointnumberLabel.setObjectName("pointnumberLabel")
        self.horizontalLayout_2.addWidget(self.pointnumberLabel)
        self.pointnumberLabel2 = QtWidgets.QLabel(self.groupBox_2)
        self.pointnumberLabel2.setObjectName("pointnumberLabel2")
        self.horizontalLayout_2.addWidget(self.pointnumberLabel2)
        
        self.coordEnterLabel = QtWidgets.QLabel(self.groupBox_2)
        self.coordEnterLabel.setObjectName("coordEnterLabel")
        self.horizontalLayout_2.addWidget(self.coordEnterLabel)
        
        self.coordinates = QtWidgets.QLineEdit(self.groupBox_2)
        self.coordinates.setObjectName("coordinates")
        self.coordinates.setText("Enter points separated by commas and space. For eg. - (0,0,0), (10,0,0), (0,20,10)")
        self.horizontalLayout_2.addWidget(self.coordinates)
        
        self.barcord = QtWidgets.QLineEdit(self.groupBox_2)
        self.barcord.setObjectName("barcord")
        self.barcord.setText("Enter coordinates for the barrier. Same format.")
        self.horizontalLayout_2.addWidget(self.barcord)
        
        self.EntButton = QtWidgets.QPushButton(self.groupBox_2)
        self.EntButton.setObjectName("Enter")
        self.horizontalLayout_2.addWidget(self.EntButton)
        self.verticalLayout.addWidget(self.groupBox_2)
     ################################################################   
        self.tabWidget.addTab(self.ML, "")
       
     ######################################################################
        self.GD = QtWidgets.QWidget()
        self.GD.setObjectName("GD")


        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(2)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_12.setText(_translate("MainWindow", "SELECT PROBE DRIVE:"))
        self.label_13.setText(_translate("MainWindow", "DEFINE NEW PROBE DRIVE SETUP:"))
        self.lineEdit_9.setText(_translate("MainWindow", "Template Name"))
        self.AxesBox.setItemText(0, _translate("MainWindow", "X-Y"))
        self.AxesBox.setItemText(1, _translate("MainWindow", "X-Y-Z"))
        self.AxesBox.setItemText(2, _translate("MainWindow", "X-ϴ"))
        self.label_14.setText(_translate("MainWindow", "Select Probe Axes:"))
        self.label_15.setText(_translate("MainWindow", "Enter IP-addresses of axis motors:"))
        self.IPBox.setTitle(_translate("MainWindow", "IP-addresses:"))
        
        self.xmotorLabel.setText(_translate("MainWindow", "X-motor"))
        self.ymotorLabel.setText(_translate("MainWindow", "Y-motor"))
        self.zmotorLabel.setText(_translate("MainWindow", "Z-motor"))
        
        self.label_18.setText(_translate("MainWindow", "Enter Encoder-Motor Counts/Step:"))
        self.label_19.setText(_translate("MainWindow", "Enter Steps/Revolution: "))
        self.label_20.setText(_translate("MainWindow", "Select Rod Threading:"))
        self.label_21.setText(_translate("MainWindow", "If custom, please specify-"))
        self.label_22.setText(_translate("MainWindow", "Calculated Steps/cm :"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.PD), _translate("MainWindow", "Probe Drive Config"))
        self.label_23.setText(_translate("MainWindow", "SELECT PROBE:"))
        self.label_24.setText(_translate("MainWindow", "CONFIGURE NEW PROBE:"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.PC), _translate("MainWindow", "Probe Config"))
        self.groupBox.setTitle(_translate("MainWindow", ""))
        self.label.setText(_translate("MainWindow", "Choose Bounding Shape"))

        self.modeBox.setItemText(0, _translate("MainWindow", "Rectangle"))
        self.modeBox.setItemText(1, _translate("MainWindow", "Circle"))
        self.modeBox.setItemText(2, _translate("MainWindow", "Line"))
        self.modeBox.setItemText(3, _translate("MainWindow", "Polygon"))
        self.modeBox.setItemText(4, _translate("MainWindow", "Ellipse"))
        self.modeBox.setItemText(5, _translate("MainWindow", "Barrier"))
        self.modeBox.setToolTip(_translate("MainWindow", "RECTANGLE: Click and Drag to define a rectangular area\n\
                                           CIRCLE: Click and Drag to define a circular area\n\
                                           ELLIPSE: Click and Drag to define a rectangle in which the ellipse will be inscribed.\n\
                                           LINE: Click, Hold and Drag to define a line path\n\
                                           POLYLINE: Click and Drag to define line path. Click again to start second line. Double click to end.\n\
                                           BARRIER: Click, Hold and Drag to define a barrier for the probe.\n\
                                               "))
                                
    
        self.gridBox.setToolTip(_translate("MainWindow", "RECTANGLE: Select for Rectangular gridding\n\
                                           CIRCLE: Select for Circular (or cylindrical) gridding\n\
                                           ELLIPSE: Select for Elliptical gridding\n\
                                           SPHERE: Select for Spherical gridding"))
        self.label_7.setText(_translate("MainWindow", "Choose Grid-Style"))
        self.gridBox.setItemText(0, _translate("MainWindow", "Rectangle"))
        self.gridBox.setItemText(1, _translate("MainWindow", "Circular"))
        self.gridBox.setItemText(2, _translate("MainWindow", "Spherical"))
        self.gridBox.setItemText(3, _translate("MainWindow", "Elliptical"))
        self.gridCentreLabel.setText(_translate("MainWindow", "Grid-Centre:"))
        self.gridCentre.setToolTip(_translate("MainWindow", "Enter custom-center(s) in the format (x,y,z), (x1,y1,z1,) , or leave empty for default gridding (Centers of defined regions)"))

        self.generatorlabel.setText(_translate("MainWindow", "Auto-generate Bounding shape?"))

        self.gridResLabel.setText(_translate("MainWindow", "Grid-Resolution"))
        self.zrangelabel.setText(_translate("MainWindow", "Z-range:"))
        self.label_11.setText(_translate("MainWindow", "to:"))
        
        self.z1.setText(_translate("MainWindow", "1"))
        self.z2.setText(_translate("MainWindow", "1"))
        self.xreslabel.setText(_translate("MainWindow", "dx (cm)"))
        self.yreslabel.setText(_translate("MainWindow", "dy (cm)"))
        self.zreslabel.setText(_translate("MainWindow", "dz (cm)"))
        self.xres.setText(_translate("MainWindow", "1"))
        self.yres.setText(_translate("MainWindow", "1"))
        self.zres.setText(_translate("MainWindow", "1"))

        self.handlabel.setText(_translate("MainWindow", "Probe Chirality"))

        self.printButton.setText(_translate("MainWindow", "Print"))
        self.printButton.setToolTip(_translate("MainWindow", "Display Data Aquisition Points"))
        self.clearButton.setText(_translate("MainWindow", "Clear"))
        self.verifyButton.setText(_translate("MainWindow", "Verify Motion List"))
        self.verifyButton.setToolTip(_translate("MainWindow", "You must print positions before verifying."))

        self.saveButton.setText(_translate("MainWindow", "Save"))
        self.saveButton.setToolTip(_translate("MainWindow", "You must verify the motion list before saving it."))

        self.EntButton.setText(_translate("MainWindow", "Enter"))
        self.EntButton.setToolTip(_translate("MainWindow", "Enter endpoints of desired geometry to denote probe-area."))

        self.groupBox_2.setTitle(_translate("MainWindow", ""))
        self.cursorLabel.setText(_translate("MainWindow", "Cursor Coordinates:"))
        self.coordLabel.setText(_translate("MainWindow", "(,)"))
        self.pointnumberLabel.setText(_translate("MainWindow", "Number of points defined: "))
        self.pointnumberLabel2.setText(_translate("MainWindow", "0"))
        self.coordEnterLabel.setText(_translate("MainWindow", "Input Coordinates here:"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.ML), _translate("MainWindow", "Motion List Generator"))
     

        self.hand.setToolTip(_translate("MainWindow", "Toggle if probe entry is from the other side?."))
