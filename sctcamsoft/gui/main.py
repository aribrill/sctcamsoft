#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue May 15 22:01:54 2018

@author: weidong
"""

# -*- coding: utf-8 -*-  

import argparse
import sys
import yaml
  
from PyQt5 import QtCore, QtWidgets, QtGui
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

    send_command = QtCore.pyqtSignal(str)

    def __init__(self):      
        super(mywindow,self).__init__()      
        self.setupUi(self)

        # Start the server-handler thread. Connect a pyqtSignal to
        # the send_command slot
        self._server_handler = ServerIO(ui_config['host'], 
                                        ui_config['input_port'], 
                                        ui_config['output_port'], 
                                        ui_config['header_length'],
                                        commands)
        self._server_handler.start()
        self.send_command.connect(self._server_handler.send_command)

        # Start a timer, provided to controls objects so they
        # can check for stale values
        self.timer_1000 = QtCore.QTimer()
        self.timer_1000.start(1000)
        
        self.Module1=Module(5,5,100,self.pushButton,self.checkbox,self.graphicsView,self.graphicsView_2,self.graphicsView_3)

        # Tell the server to start sending updates
        self.send_command.emit('connect_devices')
        self.send_command.emit('set_alerts')
        self.send_command.emit('set_monitoring')
        
        self.fan = FanControls(
            self.pushButton_2, self.pushButton_3,
            self.lineEdit_3, self.lineEdit_4, 
            self.fanAlertLineEdit, self._server_handler.on_update,
            self.timer_1000.timeout, self.send_command)

        self.power = PowerControls(
            self.pushButton_4, self.pushButton_5,
            self.lineEdit_5, self.lineEdit_6,
            self._server_handler.on_update, self.send_command)

app = QtWidgets.QApplication(sys.argv)
window = mywindow()
window.show()
sys.exit(app.exec_())
