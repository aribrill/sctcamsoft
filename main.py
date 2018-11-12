#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue May 15 22:01:54 2018

@author: weidong
"""

# -*- coding: utf-8 -*-  
  
from PyQt5 import QtWidgets, QtGui
import sys
import user_input
from dialog import Ui_Dialog
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtCore import pyqtSignal

class Figure_Canvas(FigureCanvas): #https://matplotlib.org/users/artists.html
   def __init__(self, fig):
        self.fig=fig
        FigureCanvas.__init__(self, self.fig)  # initialize father class
        self.axes = self.fig.add_subplot(1, 1,1)  # call add_subplot method in figure，(similiar to subplot method in matplotlib.pyplot)

   def test(self,data):
       self.data = data
       self.im=self.axes.imshow(data,interpolation='nearest')

class Module():
    def __init__(self, length, width, dpi):
        self.length=length
        self.width = width
        self.dpi = dpi
    def currents_update(self):
    #    dr = Figure_Canvas(Figure(figsize=(self.length, self.width), dpi=self.dpi))
        dr = Figure_Canvas(Figure(figsize=(5,5), dpi=100))
        data1 = np.random.random(size=(5, 5))
        dr.test(data1)
        dr.fig.colorbar(dr.im)  # fig.colorbar must have a image name
        graphicscene = QtWidgets.QGraphicsScene()
        graphicscene.addWidget(dr)
        self.graphicsView.setScene(graphicscene)
        self.graphicsView.show()

class Fans():
    def __init__(self):
        pass
    def Fans_on(self):
        user_input.send_command('start_fans')
    def Fans_off(self):
        user_input.send_command('stop_fans')

class Camera_power():
    def __init__(self):
        pass
    def Camera_power_on(self):
        user_input.send_command('start_camera_power')
    def Camera_power_off(self):
        user_input.send_command('stop_camera_power')


class mywindow(QtWidgets.QWidget,Ui_Dialog,Module,Fans,Camera_power):
    def __init__(self):
        super(mywindow,self).__init__()  #parent class QWidget
        self.setupUi(self)
        # # signal connect
        self.pushButton.clicked.connect(self.currents_update) #update
        self.pushButton_2.clicked.connect(self.Fans_on)
        self.pushButton_3.clicked.connect(self.Fans_off)
        self.pushButton_4.clicked.connect(self.Camera_power_on)
        self.pushButton_5.clicked.connect(self.Camera_power_off)


app = QtWidgets.QApplication(sys.argv)
window = mywindow()
window.show()
sys.exit(app.exec_())








