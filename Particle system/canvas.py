import wx
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas


class CanvasPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent, size=(800, 480))
        matplotlib.rc('axes', edgecolor='black', linewidth=1)
        self._figure = Figure()
        self._axes = self._figure.add_axes([0, 0, 1, 1])
        self._canvas = FigureCanvas(self, id=-1, figure=self._figure)
        self._figure.set_canvas(self._canvas)
        self._scat = None
        box_sizer = wx.BoxSizer(wx.VERTICAL)
        box_sizer.Add(self._canvas, flag=wx.EXPAND | wx.TOP, border=6)
        self.SetSizer(box_sizer)
        self.Fit()

    def draw_markers(self, marker_positions, marker_sizes, marker_colors):
        self._axes.clear()
        self._scat = self._axes.scatter(x=marker_positions[:, 0], y=marker_positions[:, 1],
                                        s=marker_sizes, facecolors=marker_colors)
        self._canvas.draw()
