import wx
from canvas import CanvasPanel
from wx.lib.masked import NumCtrl


class Form(wx.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._panel = wx.Panel(self)
        self._panel_sizer = wx.GridBagSizer()
        ctrl_size = (35, -1)
        value = 10
        self._init_emitter_block(ctrl_size, value)
        self._init_particle_block(ctrl_size, value)
        self._init_method_block()
        self._init_operations_block()
        self._init_canvas_block()
        self._panel.SetSizer(self._panel_sizer)
        self._panel_sizer.Fit(self)
        self.Show()

    def _init_emitter_block(self, ctrl_size, value):
        static_box = wx.StaticBox(self._panel, label="Emitter")
        box_sizer = wx.StaticBoxSizer(static_box, wx.VERTICAL)

        temp_sizer = wx.GridBagSizer(3, 4)
        text = wx.StaticText(self._panel, label="X coord")
        temp_sizer.Add(text, pos=(0, 0), flag=wx.ALIGN_CENTER | wx.ALL, border=2)
        num_ctrl = NumCtrl(self._panel, size=ctrl_size, autoSize=False, style=wx.TE_CENTER,
                           value=value, min=1, max=50, integerWidth=2, limitOnFieldChange=True)
        temp_sizer.Add(num_ctrl, pos=(0, 1), flag=wx.ALIGN_CENTER | wx.ALL, border=2)
        text = wx.StaticText(self._panel, label=" Y coord")
        temp_sizer.Add(text, pos=(0, 2), flag=wx.ALIGN_CENTER | wx.ALL, border=2)
        num_ctrl = NumCtrl(self._panel, size=ctrl_size, autoSize=False, style=wx.TE_CENTER,
                           value=value, min=1, max=50, integerWidth=2, limitOnFieldChange=True)
        temp_sizer.Add(num_ctrl, pos=(0, 3), flag=wx.ALIGN_CENTER | wx.ALL, border=2)

        text = wx.StaticText(self._panel, label="U direct")
        temp_sizer.Add(text, pos=(1, 0), flag=wx.ALIGN_CENTER | wx.ALL, border=2)
        num_ctrl = NumCtrl(self._panel, size=ctrl_size, autoSize=False,
                           style=wx.TE_CENTER, signedForegroundColour='Black',
                           value=value, min=-10, max=10, integerWidth=2, limitOnFieldChange=True)
        temp_sizer.Add(num_ctrl, pos=(1, 1), flag=wx.ALIGN_CENTER | wx.ALL, border=2)
        text = wx.StaticText(self._panel, label=" V direct")
        temp_sizer.Add(text, pos=(1, 2), flag=wx.ALIGN_CENTER | wx.ALL, border=2)
        num_ctrl = NumCtrl(self._panel, size=ctrl_size, autoSize=False,
                           style=wx.TE_CENTER, signedForegroundColour='Black',
                           value=value, min=-10, max=10, integerWidth=2, limitOnFieldChange=True)
        temp_sizer.Add(num_ctrl, pos=(1, 3), flag=wx.ALIGN_CENTER | wx.ALL, border=2)

        button = wx.Button(self._panel, label="Create emitter")
        temp_sizer.Add(button, pos=(2, 0), span=(1, 4),
                       flag=wx.EXPAND | wx.ALL, border=2)

        box_sizer.Add(temp_sizer, flag=wx.EXPAND | wx.ALL, border=1)
        self._panel_sizer.Add(box_sizer, pos=(0, 0), span=(1, 4),
                              flag=wx.EXPAND | wx.ALL, border=6)

    def _init_particle_block(self, ctrl_size, value):
        static_box = wx.StaticBox(self._panel, label="Particle")
        box_sizer = wx.StaticBoxSizer(static_box, wx.VERTICAL)

        temp_sizer = wx.GridBagSizer(4, 4)
        text = wx.StaticText(self._panel, label="U speed")
        temp_sizer.Add(text, pos=(0, 0), flag=wx.ALIGN_CENTER | wx.ALL, border=2)
        num_ctrl = NumCtrl(self._panel, size=ctrl_size, autoSize=False, style=wx.TE_CENTER,
                           value=value, min=1, max=10, integerWidth=2, limitOnFieldChange=True)
        temp_sizer.Add(num_ctrl, pos=(0, 1), flag=wx.ALIGN_CENTER | wx.ALL, border=2)
        text = wx.StaticText(self._panel, label="V speed")
        temp_sizer.Add(text, pos=(0, 2), flag=wx.ALIGN_CENTER | wx.ALL, border=2)
        num_ctrl = NumCtrl(self._panel, size=ctrl_size, autoSize=False, style=wx.TE_CENTER,
                           value=value, min=1, max=10, integerWidth=2, limitOnFieldChange=True)
        temp_sizer.Add(num_ctrl, pos=(0, 3), flag=wx.ALIGN_CENTER | wx.ALL, border=2)

        text = wx.StaticText(self._panel, label="Color")
        temp_sizer.Add(text, pos=(1, 0), flag=wx.ALIGN_CENTER | wx.ALL, border=2)
        button = wx.Button(self._panel, style=wx.BORDER_NONE | wx.BU_EXACTFIT)
        button.Bind(wx.EVT_BUTTON, self._on_color_dialog_click)
        button.SetBackgroundColour(wx.BLACK)
        temp_sizer.Add(button, pos=(1, 1), flag=wx.EXPAND | wx.ALL, border=2)

        text = wx.StaticText(self._panel, label="Lifetime")
        temp_sizer.Add(text, pos=(1, 2), flag=wx.ALIGN_CENTER | wx.ALL, border=2)
        num_ctrl = NumCtrl(self._panel, size=ctrl_size, autoSize=False, style=wx.TE_CENTER,
                           value=value, min=10, max=50, integerWidth=2, limitOnFieldChange=True)
        temp_sizer.Add(num_ctrl, pos=(1, 3), flag=wx.ALIGN_CENTER | wx.ALL, border=2)

        text = wx.StaticText(self._panel, label="Weight")
        temp_sizer.Add(text, pos=(2, 0), flag=wx.ALIGN_CENTER | wx.ALL, border=2)
        slider = wx.Slider(self._panel, value=50, minValue=1, maxValue=100,
                           style=wx.SL_HORIZONTAL | wx.SL_VALUE_LABEL)
        temp_sizer.Add(slider, pos=(2, 1), span=(1, 3),
                       flag=wx.EXPAND | wx.ALL, border=2)

        button = wx.Button(self._panel, label="Generate particle")
        temp_sizer.Add(button, pos=(3, 0), span=(1, 4),
                       flag=wx.EXPAND | wx.ALL, border=2)

        box_sizer.Add(temp_sizer, flag=wx.EXPAND | wx.ALL, border=1)
        self._panel_sizer.Add(box_sizer, pos=(1, 0), span=(1, 4),
                              flag=wx.EXPAND | wx.ALL, border=6)

    def _init_method_block(self):
        static_box = wx.StaticBox(self._panel, label="Method")
        box_sizer = wx.StaticBoxSizer(static_box, wx.VERTICAL)

        methods = ['Odeint', 'Verle']
        combo_box = wx.ComboBox(self._panel, choices=methods, value=methods[0], style=wx.CB_READONLY)
        box_sizer.Add(combo_box, flag=wx.EXPAND | wx.ALL, border=4)
        self._panel_sizer.Add(box_sizer, pos=(2, 0), span=(1, 4),
                              flag=wx.EXPAND | wx.ALL, border=6)

    def _init_operations_block(self):
        static_box = wx.StaticBox(self._panel, label="Operations")
        box_sizer = wx.StaticBoxSizer(static_box, wx.VERTICAL)

        temp_sizer = wx.GridBagSizer(3, 2)
        button = wx.Button(self._panel, label="Generate")
        temp_sizer.Add(button, pos=(0, 0), flag=wx.ALIGN_CENTER | wx.ALL, border=1)
        num_ctrl = NumCtrl(self._panel, size=(86, 24), autoSize=False, style=wx.TE_CENTER,
                           value=10, min=1, max=50, integerWidth=2, limitOnFieldChange=True)
        temp_sizer.Add(num_ctrl, pos=(0, 1), flag=wx.ALIGN_CENTER | wx.TOP, border=1)

        button = wx.Button(self._panel, label="Load")
        temp_sizer.Add(button, pos=(1, 0), flag=wx.ALIGN_CENTER | wx.ALL, border=1)
        button = wx.Button(self._panel, label="Clear")
        temp_sizer.Add(button, pos=(1, 1), flag=wx.ALIGN_CENTER | wx.ALL, border=1)

        button = wx.Button(self._panel, label="Start")
        temp_sizer.Add(button, pos=(2, 0), flag=wx.ALIGN_CENTER | wx.ALL, border=1)
        button = wx.Button(self._panel, label="Stop")
        temp_sizer.Add(button, pos=(2, 1), flag=wx.ALIGN_CENTER | wx.ALL, border=1)

        box_sizer.Add(temp_sizer, flag=wx.EXPAND | wx.ALL, border=1)
        self._panel_sizer.Add(box_sizer, pos=(3, 0), span=(1, 4),
                              flag=wx.EXPAND | wx.ALL, border=6)

    def _init_canvas_block(self):
        self._canvas = CanvasPanel(self._panel)
        self._panel_sizer.Add(self._canvas, pos=(0, 4), span=(4, 1),
                              flag=wx.EXPAND | wx.TOP | wx.RIGHT, border=8)

    def _on_color_dialog_click(self, event):
        dialog = wx.ColourDialog(self)
        dialog.GetColourData().SetChooseFull(True)

        if dialog.ShowModal() == wx.ID_OK:
            data = dialog.GetColourData()
            button = event.GetEventObject()
            button.SetBackgroundColour(data.GetColour().Get())
        dialog.Destroy()
