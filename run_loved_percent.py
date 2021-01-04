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
            widget    = pyqtgraph.PlotWidget(title='% of Maps Loved vs % Yes Threashold'),
        )

        self.__create_graph(
            graph_id  = 'taiko',
            pos       = 'right',
            widget    = pyqtgraph.PlotWidget(title='% of Maps Loved vs % Yes Threashold'),
        )

        self.__create_graph(
            graph_id  = 'catch',
            pos       = 'bottom',
            widget    = pyqtgraph.PlotWidget(title='% of Maps Loved vs % Yes Threashold'),
        )

        self.__create_graph(
            graph_id  = 'mania',
            pos       = 'right',
            relative_to=self.graphs['catch']['dock'],
            widget    = pyqtgraph.PlotWidget(title='% of Maps Loved vs % Yes Threashold'),
        )

        self.graphs['std']['widget'].setLabel('left', '% of Maps Loved')
        self.graphs['std']['widget'].setLabel('bottom', '% Yes Threshold')
        
        self.graphs['taiko']['widget'].setLabel('left', '% of Maps Loved')
        self.graphs['taiko']['widget'].setLabel('bottom', '% Yes Threshold')

        self.graphs['catch']['widget'].setLabel('left', '% of Maps Loved')
        self.graphs['catch']['widget'].setLabel('bottom', '% Yes Threshold')

        self.graphs['mania']['widget'].setLabel('left', '% of Maps Loved')
        self.graphs['mania']['widget'].setLabel('bottom', '% Yes Threshold')

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
        percent_threshold = np.linspace(0, 1, 1000)

        # Std processing
        std_yes_percent = yes_votes[self.std_gamemode_mask] / (yes_votes[self.std_gamemode_mask] + no_votes[self.std_gamemode_mask])
        xv, yv = np.meshgrid(percent_threshold, std_yes_percent)
        std_loved_passing = np.count_nonzero(yv >= xv, axis=0)/len(std_yes_percent)

        # Taiko processing
        taiko_yes_percent = yes_votes[self.taiko_gamemode_mask] / (yes_votes[self.taiko_gamemode_mask] + no_votes[self.taiko_gamemode_mask])
        xv, yv = np.meshgrid(percent_threshold, taiko_yes_percent)
        taiko_loved_passing = np.count_nonzero(yv >= xv, axis=0)/len(taiko_yes_percent)

        # Catch processing
        catch_yes_percent = yes_votes[self.catch_gamemode_mask] / (yes_votes[self.catch_gamemode_mask] + no_votes[self.catch_gamemode_mask])
        xv, yv = np.meshgrid(percent_threshold, catch_yes_percent)
        catch_loved_passing = np.count_nonzero(yv >= xv, axis=0)/len(catch_yes_percent)

        ## Mania processing
        mania_yes_percent = yes_votes[self.mania_gamemode_mask] / (yes_votes[self.mania_gamemode_mask] + no_votes[self.mania_gamemode_mask])
        xv, yv = np.meshgrid(percent_threshold, mania_yes_percent)
        mania_loved_passing = np.count_nonzero(yv >= xv, axis=0)/len(mania_yes_percent)

        # Graphing
        self.graphs['std']['plot'].setData(percent_threshold[std_loved_passing < 1], std_loved_passing[std_loved_passing < 1], pen='y')
        self.graphs['taiko']['plot'].setData(percent_threshold[std_loved_passing < 1], taiko_loved_passing[std_loved_passing < 1], pen='y')
        self.graphs['catch']['plot'].setData(percent_threshold[std_loved_passing < 1], catch_loved_passing[std_loved_passing < 1], pen='y')
        self.graphs['mania']['plot'].setData(percent_threshold[std_loved_passing < 1], mania_loved_passing[std_loved_passing < 1], pen='y')

        # Print out
        print('Std:')
        print(f' 100%: {percent_threshold[std_loved_passing < 1.00][0]}')
        print(f'  95%: {percent_threshold[std_loved_passing < 0.95][0]}')
        print(f'  90%: {percent_threshold[std_loved_passing < 0.90][0]}')
        print(f'  85%: {percent_threshold[std_loved_passing < 0.85][0]}')
        print(f'  80%: {percent_threshold[std_loved_passing < 0.80][0]}')
        print(f'  75%: {percent_threshold[std_loved_passing < 0.75][0]}')
        print(f'  50%: {percent_threshold[std_loved_passing < 0.50][0]}')
        print()
        print('Taiko:')
        print(f' 100%: {percent_threshold[taiko_loved_passing < 1.00][0]}')
        print(f'  95%: {percent_threshold[taiko_loved_passing < 0.95][0]}')
        print(f'  90%: {percent_threshold[taiko_loved_passing < 0.90][0]}')
        print(f'  85%: {percent_threshold[taiko_loved_passing < 0.85][0]}')
        print(f'  80%: {percent_threshold[taiko_loved_passing < 0.80][0]}')
        print(f'  75%: {percent_threshold[taiko_loved_passing < 0.75][0]}')
        print(f'  50%: {percent_threshold[taiko_loved_passing < 0.50][0]}')
        print()
        print('Catch:')
        print(f' 100%: {percent_threshold[catch_loved_passing < 1.00][0]}')
        print(f'  95%: {percent_threshold[catch_loved_passing < 0.95][0]}')
        print(f'  90%: {percent_threshold[catch_loved_passing < 0.90][0]}')
        print(f'  85%: {percent_threshold[catch_loved_passing < 0.85][0]}')
        print(f'  80%: {percent_threshold[catch_loved_passing < 0.80][0]}')
        print(f'  75%: {percent_threshold[catch_loved_passing < 0.75][0]}')
        print(f'  50%: {percent_threshold[catch_loved_passing < 0.50][0]}')
        print()
        print('Mania:')
        print(f' 100%: {percent_threshold[mania_loved_passing < 1.00][0]}')
        print(f'  95%: {percent_threshold[mania_loved_passing < 0.95][0]}')
        print(f'  90%: {percent_threshold[mania_loved_passing < 0.90][0]}')
        print(f'  85%: {percent_threshold[mania_loved_passing < 0.85][0]}')
        print(f'  80%: {percent_threshold[mania_loved_passing < 0.80][0]}')
        print(f'  75%: {percent_threshold[mania_loved_passing < 0.75][0]}')
        print(f'  50%: {percent_threshold[mania_loved_passing < 0.50][0]}')
        print()
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex  = MainWindow()
    sys.exit(app.exec_())