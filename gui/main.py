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

from dialog import Ui_Dialog
from server_io import ServerIO
from fan_controls import FanControls
from power_controls import PowerControls
from Module import Module

parser = argparse.ArgumentParser()
parser.add_argument('config_file', help='Path to slow control config file')
parser.add_argument('commands_file', help='Path to slow control commands file')
args = parser.parse_args()

with open(args.config_file, 'r') as config_file:
    config = yaml.load(config_file)
    ui_config = config['user_interface']

with open(args.commands_file, 'r') as commands_file:
    commands = yaml.load(commands_file)

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

