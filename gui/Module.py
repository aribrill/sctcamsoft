
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal

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


#add another frame with three status( ok warning and alert!)