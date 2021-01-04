import sys

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import pyqtgraph
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.dockarea import DockArea

from scipy import stats

import numpy as np
np.set_printoptions(suppress=True, formatter={ 'float_kind' : '{:0.2f}'.format })



ROUND         = 0
END_TIME      = 1
GAMEMODE      = 2
BEATMAPSET_ID = 3
TOPIC_ID      = 4
NUM_YES       = 5
NUM_NO        = 6

STD_GAMEMODE   = 0
TAIKO_GAMEMODE = 1
CATCH_GAMEMODE = 2
MANIA_GAMEMODE = 3


class MainWindow(QtGui.QMainWindow):
    
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        with open('data/player_skills.npy', 'rb') as f:
            self.poll_data = np.load(f)

        self.std_gamemode_mask    = (self.poll_data[:, GAMEMODE] == STD_GAMEMODE)
        self.taiko_gamemode_mask  = (self.poll_data[:, GAMEMODE] == TAIKO_GAMEMODE)
        self.catch_gamemode_mask  = (self.poll_data[:, GAMEMODE] == CATCH_GAMEMODE)
        self.mania_gamemode_mask  = (self.poll_data[:, GAMEMODE] == MANIA_GAMEMODE)

        self.__init_gui()
        self.__graph_results()

        self.show()

    
    def __init_gui(self):
        self.graphs = {}
        self.area = DockArea()

        self.__create_graph(
            graph_id  = 'std',
            pos       = 'top',
            widget    = pyqtgraph.PlotWidget(title='Std participation vs % Yes votes'),
        )

        self.std_mean_plot = self.graphs['std']['widget'].plot()
        self.std_mean_plot.setZValue(10)

        self.__create_graph(
            graph_id  = 'taiko',
            pos       = 'right',
            widget    = pyqtgraph.PlotWidget(title='Taiko participation vs % Yes votes'),
        )

        self.taiko_mean_plot = self.graphs['taiko']['widget'].plot()
        self.taiko_mean_plot.setZValue(10)

        self.__create_graph(
            graph_id  = 'catch',
            pos       = 'bottom',
            widget    = pyqtgraph.PlotWidget(title='Catch participation vs % Yes votes'),
        )

        self.catch_mean_plot = self.graphs['catch']['widget'].plot()

        self.__create_graph(
            graph_id  = 'mania',
            pos       = 'right',
            relative_to=self.graphs['catch']['dock'],
            widget    = pyqtgraph.PlotWidget(title='Mania participation vs % Yes votes'),
        )

        self.mania_mean_plot = self.graphs['mania']['widget'].plot()
        self.mania_mean_plot.setZValue(10)

        self.graphs['std']['widget'].setLabel('left', '% Yes')
        self.graphs['std']['widget'].setLabel('bottom', '# Total Votes')
        
        self.graphs['taiko']['widget'].setLabel('left', '% Yes')
        self.graphs['taiko']['widget'].setLabel('bottom', '# Total Votes')

        self.graphs['catch']['widget'].setLabel('left', '% Yes')
        self.graphs['catch']['widget'].setLabel('bottom', '# Total Votes')

        self.graphs['mania']['widget'].setLabel('left', '% Yes')
        self.graphs['mania']['widget'].setLabel('bottom', '# Total Votes')

        self.setCentralWidget(self.area)


    def __create_graph(self, graph_id=None, dock_name=' ', pos='bottom', relative_to=None, widget=None):
        if widget == None:
            widget = pyqtgraph.PlotWidget()

        widget.getViewBox().enableAutoRange()
        
        dock = pyqtgraph.dockarea.Dock(dock_name, size=(500,400))
        dock.addWidget(widget)
        self.area.addDock(dock, pos, relativeTo=relative_to)

        self.graphs[graph_id] = {
            'widget' : widget,
            'dock'   : dock,
            'plot'   : widget.plot()
        }
    

    def __graph_results(self):
        yes_votes = self.poll_data[:, NUM_YES]
        no_votes = self.poll_data[:, NUM_NO]

        # Std processing
        std_yes_votes = yes_votes[self.std_gamemode_mask]
        std_no_votes = no_votes[self.std_gamemode_mask]
        std_votes = std_yes_votes + std_no_votes

        std_sort_idx = np.argsort(std_votes)
        std_votes = std_votes[std_sort_idx]
        std_yes_votes = std_yes_votes[std_sort_idx]

        std_mean_yes_votes_percent, std_bin_votes, _ = stats.binned_statistic(std_votes, std_yes_votes/std_votes, statistic='mean', bins=20)
        
        #heatmap, _, _ = np.histogram2d(std_votes, std_yes_votes/std_votes, bins=[ 40, 20 ])
        #print(np.where(heatmap == np.max(heatmap)))
        #heatmap_img = pyqtgraph.ImageItem(heatmap, compositionMode=QtGui.QPainter.CompositionMode_Plus)
        #heatmap_img.setRect(QRectF(min(std_votes), min(std_yes_votes/std_votes), max(std_votes) - min(std_votes), max(std_yes_votes/std_votes) - min(std_yes_votes/std_votes)))
        #heatmap_img.setParentItem(self.graphs['std']['plot'])
        #self.graphs['std']['widget'].addItem(heatmap_img)

        # Taiko processing
        taiko_yes_votes = yes_votes[self.taiko_gamemode_mask]
        taiko_no_votes = no_votes[self.taiko_gamemode_mask]
        taiko_votes = taiko_yes_votes + taiko_no_votes

        taiko_sort_idx = np.argsort(taiko_votes)
        taiko_votes = taiko_votes[taiko_sort_idx]
        taiko_yes_votes = taiko_yes_votes[taiko_sort_idx]

        taiko_mean_yes_votes_percent, taiko_bin_votes, _ = stats.binned_statistic(taiko_votes, taiko_yes_votes/taiko_votes, statistic='mean', bins=20)

        # Catch processing
        catch_yes_votes = yes_votes[self.catch_gamemode_mask]
        catch_no_votes = no_votes[self.catch_gamemode_mask]
        catch_votes = catch_yes_votes + catch_no_votes

        catch_sort_idx = np.argsort(catch_votes)
        catch_votes = catch_votes[catch_sort_idx]
        catch_yes_votes = catch_yes_votes[catch_sort_idx]

        catch_mean_yes_votes_percent, catch_bin_votes, _ = stats.binned_statistic(catch_votes, catch_yes_votes/catch_votes, statistic='mean', bins=20)

        # Mania processing
        mania_yes_votes = yes_votes[self.mania_gamemode_mask]
        mania_no_votes = no_votes[self.mania_gamemode_mask]
        mania_votes = mania_yes_votes + mania_no_votes

        mania_sort_idx = np.argsort(mania_votes)
        mania_votes = mania_votes[mania_sort_idx]
        mania_yes_votes = mania_yes_votes[mania_sort_idx]

        mania_mean_yes_votes_percent, mania_bin_votes, _ = stats.binned_statistic(mania_votes, mania_yes_votes/mania_votes, statistic='mean', bins=20)

        # Graphing
        self.graphs['std']['plot'].setData(std_votes, std_yes_votes/std_votes, pen=None, symbol='o', symbolPen=None, symbolSize=2, symbolBrush=(100, 100, 255, 200))
        self.graphs['taiko']['plot'].setData(taiko_votes, taiko_yes_votes/taiko_votes, pen=None, symbol='o', symbolPen=None, symbolSize=2, symbolBrush=(100, 100, 255, 200))
        self.graphs['catch']['plot'].setData(catch_votes, catch_yes_votes/catch_votes, pen=None, symbol='o', symbolPen=None, symbolSize=2, symbolBrush=(100, 100, 255, 200))
        self.graphs['mania']['plot'].setData(mania_votes, mania_yes_votes/mania_votes, pen=None, symbol='o', symbolPen=None, symbolSize=2, symbolBrush=(100, 100, 255, 200))

        self.std_mean_plot.setData(std_bin_votes[:-1], std_mean_yes_votes_percent, pen=pyqtgraph.mkPen(color=(255, 255, 0, 100)))
        self.taiko_mean_plot.setData(taiko_bin_votes[:-1], taiko_mean_yes_votes_percent, pen=pyqtgraph.mkPen(color=(255, 255, 0, 100)))
        self.catch_mean_plot.setData(catch_bin_votes[:-1], catch_mean_yes_votes_percent, pen=pyqtgraph.mkPen(color=(255, 255, 0, 100)))
        self.mania_mean_plot.setData(mania_bin_votes[:-1], mania_mean_yes_votes_percent, pen=pyqtgraph.mkPen(color=(255, 255, 0, 100)))
      

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex  = MainWindow()
    sys.exit(app.exec_())