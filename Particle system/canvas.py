import wx
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas


class CanvasPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent, size=(800, 480))
        matplotlib.rc('axes', edgecolor='black', linewidth=1)
        self.figure = Figure()
        self._axes = self.figure.add_axes([0, 0, 1, 1])
        self._axes.set(xlim=(0, 1), ylim=(0, 1))
        self._scat = self._axes.scatter(x=[], y=[])
        self._canvas = FigureCanvas(self, id=-1, figure=self.figure)
        self.figure.set_canvas(self._canvas)
        box_sizer = wx.BoxSizer(wx.VERTICAL)
        box_sizer.Add(self._canvas, flag=wx.EXPAND | wx.TOP, border=6)
        self.SetSizer(box_sizer)
        self.Fit()

    def draw_markers(self, marker_positions, marker_sizes, marker_colors):
        self._scat.set_offsets(marker_positions)
        self._scat.set_sizes(marker_sizes)
        self._scat.set_facecolors(marker_colors)

    def clear(self):
        self._scat.remove()
        self._scat = self._axes.scatter(x=[], y=[])
