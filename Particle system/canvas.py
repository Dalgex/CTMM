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
        box_sizer = wx.BoxSizer(wx.VERTICAL)
        box_sizer.Add(self._canvas, flag=wx.EXPAND | wx.TOP, border=6)
        self.SetSizer(box_sizer)
        self.Fit()
