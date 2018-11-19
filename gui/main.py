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
