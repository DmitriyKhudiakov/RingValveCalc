import matplotlib
matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class MatplotlibWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.sc = MplCanvas(self, width=5, height=4, dpi=100)
        self.plot_some()
        self.toolbar = NavigationToolbar(self.sc, self)
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.toolbar)
        self.vbox.addWidget(self.sc)
        self.setLayout(self.vbox)

    def plot_some(self):
        self.sc.axes.plot([0,1,2,3,4], [10,1,20,3,40])
        