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



'''
- Is there a correlation between more participation and more yes votes?
- Is there a consistent relative distribution of participation for every voting cycle, and if so, what is the distribution?
- For each voting cycle, what can be deduced from maps lacking in participation when compared to maps with most participation?
- What % yes votes is required if a certain % of all maps voted on are to be loved?
'''

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
            widget    = pyqtgraph.PlotWidget(title='Std cycle vs # total votes'),
        )

        self.__create_graph(
            graph_id  = 'taiko',
            pos       = 'right',
            widget    = pyqtgraph.PlotWidget(title='Taiko cycle vs # total votes'),
        )

        self.__create_graph(
            graph_id  = 'catch',
            pos       = 'bottom',
            widget    = pyqtgraph.PlotWidget(title='Catch cycle vs # total votes'),
        )

        self.__create_graph(
            graph_id  = 'mania',
            pos       = 'right',
            relative_to=self.graphs['catch']['dock'],
            widget    = pyqtgraph.PlotWidget(title='Mania cycle vs # total votes'),
        )

        self.graphs['std']['widget'].setLabel('left', '# Total Votes')
        self.graphs['std']['widget'].setLabel('bottom', 'Cycle')
        
        self.graphs['taiko']['widget'].setLabel('left', '# Total Votes')
        self.graphs['taiko']['widget'].setLabel('bottom', 'Cycle')

        self.graphs['catch']['widget'].setLabel('left', '# Total Votes')
        self.graphs['catch']['widget'].setLabel('bottom', 'Cycle')

        self.graphs['mania']['widget'].setLabel('left', '# Total Votes')
        self.graphs['mania']['widget'].setLabel('bottom', 'Cycle')

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
        cycle = self.poll_data[:, ROUND]

        # Std processing
        std_votes = yes_votes[self.std_gamemode_mask] + no_votes[self.std_gamemode_mask]
        std_percent_yes_votes = yes_votes[self.std_gamemode_mask]/std_votes
        std_cycle = cycle[self.std_gamemode_mask]

        # Taiko processing
        taiko_votes = yes_votes[self.taiko_gamemode_mask] + no_votes[self.taiko_gamemode_mask]
        taiko_percent_yes_votes = yes_votes[self.taiko_gamemode_mask]/taiko_votes
        taiko_cycle = cycle[self.taiko_gamemode_mask]

        # Catch processing
        catch_votes = yes_votes[self.catch_gamemode_mask] + no_votes[self.catch_gamemode_mask]
        catch_percent_yes_votes = yes_votes[self.catch_gamemode_mask]/catch_votes
        catch_cycle = cycle[self.catch_gamemode_mask]

        # Mania processing
        mania_votes = yes_votes[self.mania_gamemode_mask] + no_votes[self.mania_gamemode_mask]
        mania_percent_yes_votes = yes_votes[self.mania_gamemode_mask]/mania_votes
        mania_cycle = cycle[self.mania_gamemode_mask]

        # Scatter plot highlighting
        brush_fail = (255, 100, 100, 200)
        brush_pass = (100, 100, 255, 200)

        std_scatter_brush = [ pyqtgraph.mkBrush(brush_fail if std_percent_yes_vote <= 0.85 else brush_pass) for std_percent_yes_vote in std_percent_yes_votes ]
        taiko_scatter_brush = [ pyqtgraph.mkBrush(brush_fail if taiko_percent_yes_vote <= 0.85 else brush_pass) for taiko_percent_yes_vote in taiko_percent_yes_votes ]
        catch_scatter_brush = [ pyqtgraph.mkBrush(brush_fail if catch_percent_yes_vote <= 0.85 else brush_pass) for catch_percent_yes_vote in catch_percent_yes_votes ]
        mania_scatter_brush = [ pyqtgraph.mkBrush(brush_fail if mania_percent_yes_vote <= 0.85 else brush_pass) for mania_percent_yes_vote in mania_percent_yes_votes ]

        # Graphing
        self.graphs['std']['plot'].setData(std_cycle, std_votes, pen=None, symbol='o', symbolPen=None, symbolSize=2, symbolBrush=std_scatter_brush)
        self.graphs['taiko']['plot'].setData(taiko_cycle, taiko_votes, pen=None, symbol='o', symbolPen=None, symbolSize=2, symbolBrush=taiko_scatter_brush)
        self.graphs['catch']['plot'].setData(catch_cycle, catch_votes, pen=None, symbol='o', symbolPen=None, symbolSize=2, symbolBrush=catch_scatter_brush)
        self.graphs['mania']['plot'].setData(mania_cycle, mania_votes, pen=None, symbol='o', symbolPen=None, symbolSize=2, symbolBrush=mania_scatter_brush)


        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex  = MainWindow()
    sys.exit(app.exec_())