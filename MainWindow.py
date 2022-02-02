
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class Ui_MainWindow(object):

    
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 800)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.layoutWidget = QtWidgets.QWidget(self.centralwidget)
        # self.layoutWidget.setGeometry(QtCore.QRect(0, 0, 1131, 571))
        self.layoutWidget.setObjectName("layoutWidget")
        
        
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(2, 0, 2 , 0)
        self.verticalLayout.setObjectName("verticalLayout")
        
        
        self.Box2 = QtWidgets.QGroupBox(self.layoutWidget)
        self.Box2.setObjectName("Box2")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.Box2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        
        
        self.label = QtWidgets.QLabel(self.Box2)
        self.label.setToolTip("")
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        
        self.xres = QtWidgets.QLineEdit(self.Box2)
        self.xres.setObjectName("xres")
        self.horizontalLayout.addWidget(self.xres)
        self.xres.setText("1")
        self.xres.setValidator(QDoubleValidator())
        
        self.label_2 = QtWidgets.QLabel(self.Box2)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        
        self.yres = QtWidgets.QLineEdit(self.Box2)
        self.yres.setObjectName("yres")
        self.horizontalLayout.addWidget(self.yres)
        self.yres.setText("1")
        self.yres.setValidator(QDoubleValidator())
        
        
        self.label_5 = QtWidgets.QLabel(self.Box2)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout.addWidget(self.label_5)
        
        self.zres = QtWidgets.QLineEdit(self.Box2)
        self.zres.setObjectName("zres")
        self.horizontalLayout.addWidget(self.zres)
        self.zres.setText("1")
        self.zres.setValidator(QDoubleValidator())

        self.label_3 = QtWidgets.QLabel(self.Box2)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout.addWidget(self.label_3)
        
        self.z1 = QtWidgets.QLineEdit(self.Box2)
        self.z1.setObjectName("z1")
        self.horizontalLayout.addWidget(self.z1)
        self.z1.setText("0")
        self.z1.setValidator(QDoubleValidator())

        self.label_4 = QtWidgets.QLabel(self.Box2)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout.addWidget(self.label_4)
        
        self.z2 = QtWidgets.QLineEdit(self.Box2)
        self.z2.setObjectName("z2")
        self.horizontalLayout.addWidget(self.z2)
        self.z2.setText("1")
        self.z2.setValidator(QDoubleValidator())

        
        self.verticalLayout.addWidget(self.Box2)
        
        
             
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
       
        
       
        
        
        self.Box1 = QtWidgets.QGroupBox(self.layoutWidget)
        self.Box1.setObjectName("Box1")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.Box1)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        
   
        
        
        
        self.lineButton = QtWidgets.QPushButton(self.Box1)
        self.lineButton.setObjectName("lineButton")
        self.lineButton.setCheckable(True)
        self.verticalLayout_2.addWidget(self.lineButton)
        
        self.rectButton = QtWidgets.QPushButton(self.Box1)
        self.rectButton.setObjectName("rectButton")
        self.rectButton.setCheckable(True)
        self.verticalLayout_2.addWidget(self.rectButton)
        
        self.polylineButton = QtWidgets.QPushButton(self.Box1)
        self.polylineButton.setObjectName("polylineButton")
        self.polylineButton.setCheckable(True)
        self.verticalLayout_2.addWidget(self.polylineButton)
        
        
        
        self.printButton = QtWidgets.QPushButton(self.Box1)
        self.printButton.setObjectName("printButton")
        self.verticalLayout_2.addWidget(self.printButton)
        self.clearButton = QtWidgets.QPushButton(self.Box1)
        self.clearButton.setObjectName("clearButton")
        self.verticalLayout_2.addWidget(self.clearButton)
        self.verifyButton = QtWidgets.QPushButton(self.Box1)
        self.verifyButton.setObjectName("verifyButton")
        self.verticalLayout_2.addWidget(self.verifyButton)
        self.saveButton = QtWidgets.QPushButton(self.Box1)
        self.saveButton.setEnabled(False)
        self.saveButton.setObjectName("saveButton")
        self.verticalLayout_2.addWidget(self.saveButton)
        
        self.horizontalLayout_3.addWidget(self.Box1)

        self.verticalLayout.addLayout(self.horizontalLayout_3)
       
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(20, 650, 810, 25))
        self.widget.setObjectName("widget")
     
        
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
    
        self.label_Coord = QtWidgets.QLabel(self.widget)
        self.label_Coord.setObjectName("CoordLabel")
        self.horizontalLayout_2.addWidget(self.label_Coord)

        self.label_str = QtWidgets.QLabel(self.widget)
        self.label_str.setObjectName("Stringlabel")
        self.horizontalLayout_2.addWidget(self.label_str)
        
        self.ps = QtWidgets.QLineEdit(self.widget)
        self.ps.setObjectName("ps")
        self.ps.setFixedSize(500, 20);
        self.horizontalLayout_2.addWidget(self.ps)
        self.ps.setText("Enter points separated by commas and space. For eg. - (0,0,0), (10,0,0)")

        self.EntButton = QtWidgets.QPushButton(self.widget)
        self.EntButton.setObjectName("Enter")
        self.horizontalLayout_2.addWidget(self.EntButton)
        
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 958, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Motion List Generator"))
        self.Box2.setTitle(_translate("MainWindow", ""))
        self.label.setText(_translate("MainWindow", "x-resolution (cm)"))
        self.label_2.setText(_translate("MainWindow", "y-resolution (cm)"))
        self.label_3.setText(_translate("MainWindow", "z-range:"))
        self.label_4.setText(_translate("MainWindow", "to"))
        self.label_5.setText(_translate("MainWindow", "z-resolution (cm)"))
        self.label_str.setText(_translate("MainWindow", "Input Coordinates here"))
        self.label_Coord.setText(_translate("MainWindow", "Mouse Coordinates   "))

        self.Box1.setTitle(_translate("MainWindow", ""))
      
        self.lineButton.setText(_translate("MainWindow", "Line"))
        self.lineButton.setToolTip(_translate("MainWindow", "Click, Hold and Drag to define a line path"))

        self.rectButton.setText(_translate("MainWindow", "Rectangle"))
        self.rectButton.setToolTip(_translate("MainWindow", "Click and Drag to define a rectangular area"))

        self.polylineButton.setText(_translate("MainWindow", "Polygon"))
        self.polylineButton.setToolTip(_translate("MainWindow", "Click and Drag to define line path. Click again to start second line. Double click to end."))

        self.printButton.setToolTip(_translate("MainWindow", "Display Data Aquisition Points"))
        self.printButton.setText(_translate("MainWindow", "Print"))
        self.clearButton.setText(_translate("MainWindow", "Clear"))
        self.verifyButton.setText(_translate("MainWindow", "Verify Motion List"))
        self.verifyButton.setToolTip(_translate("MainWindow", "You must print positions before verifying."))

        self.saveButton.setText(_translate("MainWindow", "Save"))
        self.saveButton.setToolTip(_translate("MainWindow", "You must verify the motion list before saving it."))

        self.EntButton.setText(_translate("MainWindow", "Enter"))
        self.EntButton.setToolTip(_translate("MainWindow", "Enter endpoints of desired geometry to denote probe-area."))


################################################################################# 