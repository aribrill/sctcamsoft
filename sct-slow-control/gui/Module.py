
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal
import matplotlib
import matplotlib.patches as mpatches

class Figure_Canvas(FigureCanvas): #https://matplotlib.org/users/artists.html
   def __init__(self, fig):
        self.fig=fig
        FigureCanvas.__init__(self, self.fig)  # initialize father class
        self.axes = self.fig.add_subplot(1, 1,1)  # call add_subplot method in figure，(similiar to subplot method in matplotlib.pyplot)

   def display(self,data): #show 2-D data
       self.data = data
       self.im = self.axes.imshow(data, cmap="rainbow", interpolation='nearest')
       self.fig.colorbar(self.im)
   def display2(self,data):
       self.data = data
       self.im = self.axes.imshow(data, cmap="rainbow", interpolation='nearest')
       red_patch = mpatches.Patch(color='red', label='Alert')
       green_patch = mpatches.Patch(color='lightgreen', label='Warning')
       blue_patch = mpatches.Patch(color='blue', label='Ok')
       self.axes.legend(handles=[red_patch,green_patch,blue_patch],bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=3, mode="expand", borderaxespad=0.)  #loc3:‘lower left’ ncol=2: legend has 2 column


class Module():
    def __init__(self, length, width, dpi, button,checkbox,gView1,gView2,gView3):
        self.length=length
        self.width = width
        self.dpi = dpi
        self.button=button
        self.gView1 = gView1
        self.gView2 = gView2
        self.gView3 = gView3
        self.checkbox = checkbox

        self.button.clicked.connect(self.Currents_update)
        self.button.clicked.connect(self.Voltage_update)
        self.button.clicked.connect(self.Temp_update)


    def Currents_update(self):
        dr = Figure_Canvas(Figure(figsize=(self.length, self.width), dpi=self.dpi))
        data1 = np.random.random(size=(5, 5))
        if  self.checkbox.isChecked(): #if status view is on
            data1[data1<=0.3]=0 # print (data1<=0.3) is a Boolean array
            data1[(data1 > 0.3) & (data1 <= 0.6)] = 0.5
            data1[(data1 > 0.6) & (data1 <= 1)] = 1
            dr.display2(data1)
        else:
             dr.display(data1)
        graphicscene = QtWidgets.QGraphicsScene()
        graphicscene.addWidget(dr)
        self.gView1.setScene(graphicscene)
        self.gView1.show()

    def Voltage_update(self):
        dr = Figure_Canvas(Figure(figsize=(self.length, self.width), dpi=self.dpi))
        data1 = np.random.random(size=(5, 5))
        if  self.checkbox.isChecked(): #if status view is on
            data1[data1<=0.3]=0 # print (data1<=0.3) is a Boolean array
            data1[(data1 > 0.3) & (data1 <= 0.6)] = 0.5
            data1[(data1 > 0.6) & (data1 <= 1)] = 1
            dr.display2(data1)
        else:
             dr.display(data1)
        graphicscene = QtWidgets.QGraphicsScene()
        graphicscene.addWidget(dr)
        self.gView2.setScene(graphicscene)
        self.gView2.show()
    def Temp_update(self):
        dr = Figure_Canvas(Figure(figsize=(self.length, self.width), dpi=self.dpi))
        data1 = np.random.random(size=(5, 5))
        if  self.checkbox.isChecked(): #if status view is on
            data1[data1<=0.3]=0 # print (data1<=0.3) is a Boolean array
            data1[(data1 > 0.3) & (data1 <= 0.6)] = 0.5
            data1[(data1 > 0.6) & (data1 <= 1)] = 1
            dr.display2(data1)
        else:
             dr.display(data1)
        graphicscene = QtWidgets.QGraphicsScene()
        graphicscene.addWidget(dr)
        self.gView3.setScene(graphicscene)
        self.gView3.show()
