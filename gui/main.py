#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue May 15 22:01:54 2018

@author: weidong
"""

# -*- coding: utf-8 -*-  

import sys
sys.path.append("../")

import argparse
import yaml
  
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from dialog import Ui_Dialog
from server_io import ServerIO
from fan_controls import FanControls
from power_controls import PowerControls


parser = argparse.ArgumentParser()
parser.add_argument('config_file', help='Path to slow control config file')
parser.add_argument('commands_file', help='Path to slow control commands file')
args = parser.parse_args()

with open(args.config_file, 'r') as config_file:
    config = yaml.load(config_file)
    ui_config = config['user_interface']

with open(args.commands_file, 'r') as commands_file:
    commands = yaml.load(commands_file)

class Figure_Canvas(FigureCanvas): #https://matplotlib.org/users/artists.html
   def __init__(self, fig):
        self.fig=fig
        FigureCanvas.__init__(self, self.fig)  # initialize father class
        self.axes = self.fig.add_subplot(1, 1,1)  # call add_subplot method in figure，(similiar to subplot method in matplotlib.pyplot)

   def display(self,data): #show 2-D data
       self.data = data
       self.im=self.axes.imshow(data,interpolation='nearest')

class Module():
    def __init__(self, length, width, dpi, button,gView1,gView2,gView3):
        self.length=length
        self.width = width
        self.dpi = dpi
        self.button=button
        self.gView1 = gView1
        self.gView2 = gView2
        self.gView3 = gView3
        self.button.clicked.connect(self.Currents_update)
        self.button.clicked.connect(self.Voltage_update)
    def Currents_update(self):
        dr = Figure_Canvas(Figure(figsize=(self.length, self.width), dpi=self.dpi))
        data1 = np.random.random(size=(5, 5))
        dr.display(data1)
        dr.fig.colorbar(dr.im)  # fig.colorbar must have a image name
        graphicscene = QtWidgets.QGraphicsScene()
        graphicscene.addWidget(dr)
        self.gView1.setScene(graphicscene)
        self.gView1.show()
    def Voltage_update(self):
        dr = Figure_Canvas(Figure(figsize=(self.length, self.width), dpi=self.dpi))
        data1 = np.random.random(size=(5, 5))
        dr.display(data1)
        dr.fig.colorbar(dr.im)  # fig.colorbar must have a image name
        graphicscene = QtWidgets.QGraphicsScene()
        graphicscene.addWidget(dr)
        self.gView2.setScene(graphicscene)
        self.gView2.show()
    def Temp_update(self):
        dr = Figure_Canvas(Figure(figsize=(self.length, self.width), dpi=self.dpi))
        data1 = np.random.random(size=(5, 5))
        dr.display(data1)
        dr.fig.colorbar(dr.im)  # fig.colorbar must have a image name
        graphicscene = QtWidgets.QGraphicsScene()
        graphicscene.addWidget(dr)
        self.gView3.setScene(graphicscene)
        self.gView3.show()

class mywindow(QtWidgets.QWidget,Ui_Dialog):

    send_command = pyqtSignal(str)

    def __init__(self):      
        super(mywindow,self).__init__()      
        self.setupUi(self)

        self._server_handler = ServerIO(ui_config['host'], 
                                        ui_config['input_port'], 
                                        ui_config['output_port'], 
                                        commands)
        self._server_handler.start()
        self.send_command.connect(self._server_handler.send_command)

        user_input.send_command('connect_devices')
        user_input.send_command('set_monitoring')  
        # user_input.send_command('set_alerts')        
      
        self.fan = FanController(
            self.pushButton_2, self.pushButton_3,
            self.lineEdit_3, self.lineEdit_4, self.fanAlertLineEdit)
        self._server_listener.register_observer(self.fan)

        self.Module1=Module(5,5,100,self.pushButton,self.graphicsView,self.graphicsView_2,self.graphicsView_3)

        self.send_command.emit('connect_devices')
        self.send_command.emit('set_monitoring')
        
        self.fan = FanControls(
            self.pushButton_2, 
            self.pushButton_3,
            self.lineEdit_3, 
            self.lineEdit_4, 
            self.fanAlertLineEdit,
            self._server_handler.on_update,
            self.send_command)

        self.power = PowerControls(
            self.pushButton_4,
            self.pushButton_5,
            self.lineEdit_5,
            self.lineEdit_6,
            self._server_handler.on_update,
            self.send_command)

app = QtWidgets.QApplication(sys.argv)
window = mywindow()
window.show()
sys.exit(app.exec_())
