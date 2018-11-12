#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue May 15 22:01:54 2018

@author: weidong
"""

# -*- coding: utf-8 -*-  

import sys
sys.path.append("..")
  
from PyQt5 import QtWidgets, QtGui
import sys
import user_input
from dialog import Ui_Dialog
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtCore import pyqtSignal
from abc import ABC
import socket
import slow_control_pb2 as sc
from PyQt5.QtCore import QThread, pyqtSignal

class Figure_Canvas(FigureCanvas): #https://matplotlib.org/users/artists.html
   def __init__(self, fig):
        self.fig=fig
        FigureCanvas.__init__(self, self.fig)  # initialize father class
        self.axes = self.fig.add_subplot(1, 1,1)  # call add_subplot method in figure，(similiar to subplot method in matplotlib.pyplot)

   def test(self,data):
       self.data = data
       self.im=self.axes.imshow(data,interpolation='nearest')

class ServerListener(QThread):
    def __init__(self, host, output_port):
        QThread.__init__(self)

        self._observers = []

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect((host, output_port))
        
    def run(self):
        while True:
            serialized_message = self._sock.recv(1024)
            if serialized_message:
                user_update = sc.UserUpdate()
                user_update.ParseFromString(serialized_message)
                for update in user_update.updates:
                    if (update.device == 'ALERT'):
                        print("ALERT: {}".format(update.variable))
                    for observer in self._observers:
                        observer.on_update(update)

    def register_observer(self, observer):
        self._observers.append(observer)

class ServerUpdateObserver(ABC):
    def on_update(update):
        raise NotImplementedError()

class FanController(ServerUpdateObserver):

    def __init__(self, 
                 on_button, off_button, 
                 voltage_textedit, current_textedit,
                 alert_textedit):
        self._on_button = on_button
        self._off_button = off_button
        self._voltage_textedit = voltage_textedit
        self._current_textedit = current_textedit
        self._alert_textedit = alert_textedit

        self._on_button.clicked.connect(self.fans_on)
        self._off_button.clicked.connect(self.fans_off)

    def fans_on(self):
        user_input.send_command('start_fans')

    def fans_off(self):
        user_input.send_command('stop_fans')

    def voltage_update(self, new_voltage):
        self._voltage_textedit.setText(new_voltage)

    def current_update(self, new_current):
        self._current_textedit.setText(new_current)

    def draw_alert(self, state, notifcation):
        self._alert_textedit.setText(notifcation)

    def on_update(self, update):

        alert_vars = ['fan_current', 'fan_voltage']

        if (update.device == 'ALERT' and (update.variable in alert_vars)):
            self.draw_alert('alert', 'ALERT: {} {}'.format(update.variable, update.value))
        elif (update.device == 'fan'):
            self.draw_alert('ok', 'OK')
            if (update.variable == 'voltage'):
                self.voltage_update(update.value)
            elif (update.variable == 'current'):
                self.current_update(update.value)

class mywindow(QtWidgets.QWidget,Ui_Dialog):
    def __init__(self):      
        super(mywindow,self).__init__()      
        self.setupUi(self)

        self._server_listener = ServerListener("127.0.0.1", 12346)
        self._server_listener.start()
        
        user_input.send_command('connect_devices')
        user_input.send_command('set_monitoring')  
        # user_input.send_command('set_alerts')        
      
        self.fan = FanController(
            self.pushButton_2, self.pushButton_3,
            self.lineEdit_3, self.lineEdit_4, self.fanAlertLineEdit)
        self._server_listener.register_observer(self.fan)

    def Camera_power_on(self):
        user_input.send_command('start_camera_power')
    def Camera_power_off(self):
        user_input.send_command('stop_camera_power')

    def Temp_show(self):
        dr = Figure_Canvas(Figure(figsize=(5, 5), dpi=110))
        data1 = np.random.random(size=(5, 5))
        dr.test(data1)
        dr.fig.colorbar(dr.im)  # fig.colorbar must have a image name
        graphicscene = QtWidgets.QGraphicsScene()
        graphicscene.addWidget(dr)
        self.graphicsView.setScene(graphicscene)
        self.graphicsView.show()

        dr2 = Figure_Canvas(Figure(figsize=(5, 5), dpi=110))
        data2 = np.random.random(size=(5, 5))
        dr2.test(data2)
        dr2.fig.colorbar(dr2.im)  # fig.colorbar must have a image name
        graphicscene = QtWidgets.QGraphicsScene()
        graphicscene.addWidget(dr2)
        self.graphicsView_2.setScene(graphicscene)
        self.graphicsView_2.show()

        dr3 = Figure_Canvas(Figure(figsize=(5, 5), dpi=110))
        data3 = np.random.random(size=(5, 5))
        dr3.test(data3)
        dr3.fig.colorbar(dr3.im)  # fig.colorbar must have a image name
        graphicscene = QtWidgets.QGraphicsScene()
        graphicscene.addWidget(dr3)
        self.graphicsView_3.setScene(graphicscene)
        self.graphicsView_3.show()


app = QtWidgets.QApplication(sys.argv)  
window = mywindow()
window.show()
sys.exit(app.exec_())








