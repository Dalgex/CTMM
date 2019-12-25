import wx
import numpy as np
from wx.lib.masked import NumCtrl
from matplotlib.animation import FuncAnimation

from emitter import Emitter
from loading import load_data
from canvas import CanvasPanel
from gravity_simulation import calculate_particle_motion


class Form(wx.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._panel = wx.Panel(self)
        self._panel_sizer = wx.GridBagSizer()
        self._widgets = {}
        self._canvas = None
        self._max_coord = 0.0
        ctrl_size = (35, -1)
        value = 1
        self._is_calculated = False
        self._is_solar_mode = False
        self._emitter = Emitter([value, value], [value, value])

        self._init_emitter_block(ctrl_size, value)
        self._init_particle_block(ctrl_size, value)
        self._init_method_block()
        self._init_operations_block()
        self._init_canvas_block()

        self._panel.SetSizer(self._panel_sizer)
        self._panel_sizer.Fit(self)
        self.Show()
        self.animation = FuncAnimation(self._canvas.figure, self._update_canvas, interval=100)

    def _init_emitter_block(self, ctrl_size, value):
        static_box = wx.StaticBox(self._panel, label="Emitter")
        box_sizer = wx.StaticBoxSizer(static_box, wx.VERTICAL)

        temp_sizer = wx.GridBagSizer(3, 4)
        text = wx.StaticText(self._panel, label="X coord")
        temp_sizer.Add(text, pos=(0, 0), flag=wx.ALIGN_CENTER | wx.ALL, border=2)
        num_ctrl = NumCtrl(self._panel, size=ctrl_size, autoSize=False, style=wx.TE_CENTER,
                           value=value, min=0, max=99, integerWidth=2, limitOnFieldChange=True)
        self._widgets['x_coord'] = num_ctrl
        temp_sizer.Add(num_ctrl, pos=(0, 1), flag=wx.ALIGN_CENTER | wx.ALL, border=2)
        text = wx.StaticText(self._panel, label=" Y coord")
        temp_sizer.Add(text, pos=(0, 2), flag=wx.ALIGN_CENTER | wx.ALL, border=2)
        num_ctrl = NumCtrl(self._panel, size=ctrl_size, autoSize=False, style=wx.TE_CENTER,
                           value=value, min=0, max=99, integerWidth=2, limitOnFieldChange=True)
        self._widgets['y_coord'] = num_ctrl
        temp_sizer.Add(num_ctrl, pos=(0, 3), flag=wx.ALIGN_CENTER | wx.ALL, border=2)

        text = wx.StaticText(self._panel, label="U direct")
        temp_sizer.Add(text, pos=(1, 0), flag=wx.ALIGN_CENTER | wx.ALL, border=2)
        num_ctrl = NumCtrl(self._panel, size=ctrl_size, autoSize=False,
                           style=wx.TE_CENTER, signedForegroundColour='Black',
                           value=value, min=-10, max=10, integerWidth=2, limitOnFieldChange=True)
        self._widgets['u_direct'] = num_ctrl
        temp_sizer.Add(num_ctrl, pos=(1, 1), flag=wx.ALIGN_CENTER | wx.ALL, border=2)
        text = wx.StaticText(self._panel, label=" V direct")
        temp_sizer.Add(text, pos=(1, 2), flag=wx.ALIGN_CENTER | wx.ALL, border=2)
        num_ctrl = NumCtrl(self._panel, size=ctrl_size, autoSize=False,
                           style=wx.TE_CENTER, signedForegroundColour='Black',
                           value=value, min=-10, max=10, integerWidth=2, limitOnFieldChange=True)
        self._widgets['v_direct'] = num_ctrl
        temp_sizer.Add(num_ctrl, pos=(1, 3), flag=wx.ALIGN_CENTER | wx.ALL, border=2)

        button = wx.Button(self._panel, label="Change emitter")
        button.Bind(wx.EVT_BUTTON, self._on_emitter_change_click)
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
                           value=value, min=1, max=99, integerWidth=2, limitOnFieldChange=True)
        self._widgets['u_speed'] = num_ctrl
        temp_sizer.Add(num_ctrl, pos=(0, 1), flag=wx.ALIGN_CENTER | wx.ALL, border=2)
        text = wx.StaticText(self._panel, label="V speed")
        temp_sizer.Add(text, pos=(0, 2), flag=wx.ALIGN_CENTER | wx.ALL, border=2)
        num_ctrl = NumCtrl(self._panel, size=ctrl_size, autoSize=False, style=wx.TE_CENTER,
                           value=value, min=1, max=99, integerWidth=2, limitOnFieldChange=True)
        self._widgets['v_speed'] = num_ctrl
        temp_sizer.Add(num_ctrl, pos=(0, 3), flag=wx.ALIGN_CENTER | wx.ALL, border=2)

        text = wx.StaticText(self._panel, label="Color")
        temp_sizer.Add(text, pos=(1, 0), flag=wx.ALIGN_CENTER | wx.ALL, border=2)
        button = wx.Button(self._panel, style=wx.BORDER_NONE | wx.BU_EXACTFIT)
        button.Bind(wx.EVT_BUTTON, self._on_color_dialog_click)
        self._widgets['color'] = button
        button.SetBackgroundColour(wx.BLACK)
        temp_sizer.Add(button, pos=(1, 1), flag=wx.EXPAND | wx.ALL, border=2)

        text = wx.StaticText(self._panel, label="Lifetime")
        temp_sizer.Add(text, pos=(1, 2), flag=wx.ALIGN_CENTER | wx.ALL, border=2)
        num_ctrl = NumCtrl(self._panel, size=ctrl_size, autoSize=False, style=wx.TE_CENTER,
                           value=50, min=10, max=100, integerWidth=3, limitOnFieldChange=True)
        self._widgets['life_time'] = num_ctrl
        temp_sizer.Add(num_ctrl, pos=(1, 3), flag=wx.ALIGN_CENTER | wx.ALL, border=2)

        text = wx.StaticText(self._panel, label="Weight")
        temp_sizer.Add(text, pos=(2, 0), flag=wx.ALIGN_CENTER | wx.ALL, border=2)
        slider = wx.Slider(self._panel, value=50, minValue=1, maxValue=100,
                           style=wx.SL_HORIZONTAL | wx.SL_VALUE_LABEL)
        self._widgets['mass'] = slider
        temp_sizer.Add(slider, pos=(2, 1), span=(1, 3),
                       flag=wx.EXPAND | wx.ALL, border=2)

        button = wx.Button(self._panel, label="Generate particle")
        button.Bind(wx.EVT_BUTTON, self._on_single_particle_generation_click)
        temp_sizer.Add(button, pos=(3, 0), span=(1, 4),
                       flag=wx.EXPAND | wx.ALL, border=2)

        box_sizer.Add(temp_sizer, flag=wx.EXPAND | wx.ALL, border=1)
        self._panel_sizer.Add(box_sizer, pos=(1, 0), span=(1, 4),
                              flag=wx.EXPAND | wx.ALL, border=6)

    def _init_method_block(self):
        static_box = wx.StaticBox(self._panel, label="Method")
        box_sizer = wx.StaticBoxSizer(static_box, wx.VERTICAL)
        methods = ['Odeint', 'Verlet']
        combo_box = wx.ComboBox(self._panel, choices=methods, value=methods[0], style=wx.CB_READONLY)
        self._widgets['method'] = combo_box

        box_sizer.Add(combo_box, flag=wx.EXPAND | wx.ALL, border=4)
        self._panel_sizer.Add(box_sizer, pos=(2, 0), span=(1, 4),
                              flag=wx.EXPAND | wx.ALL, border=6)

    def _init_operations_block(self):
        static_box = wx.StaticBox(self._panel, label="Operations")
        box_sizer = wx.StaticBoxSizer(static_box, wx.VERTICAL)

        temp_sizer = wx.GridBagSizer(3, 2)
        button = wx.Button(self._panel, label="Generate")
        button.Bind(wx.EVT_BUTTON, self._on_random_particle_generation_click)
        temp_sizer.Add(button, pos=(0, 0), flag=wx.ALIGN_CENTER | wx.ALL, border=1)
        num_ctrl = NumCtrl(self._panel, size=(86, 24), autoSize=False, style=wx.TE_CENTER,
                           value=10, min=1, max=50, integerWidth=2, limitOnFieldChange=True)
        self._widgets['random_generation'] = num_ctrl
        temp_sizer.Add(num_ctrl, pos=(0, 1), flag=wx.ALIGN_CENTER | wx.TOP, border=1)

        button = wx.Button(self._panel, label="Load")
        button.Bind(wx.EVT_BUTTON, self._on_loading_click)
        temp_sizer.Add(button, pos=(1, 0), flag=wx.ALIGN_CENTER | wx.ALL, border=1)
        button = wx.Button(self._panel, label="Clear")
        temp_sizer.Add(button, pos=(1, 1), flag=wx.ALIGN_CENTER | wx.ALL, border=1)
        button.Bind(wx.EVT_BUTTON, self._on_clear_click)

        button = wx.Button(self._panel, label="Start")
        button.Bind(wx.EVT_BUTTON, self._on_start_click)
        temp_sizer.Add(button, pos=(2, 0), flag=wx.ALIGN_CENTER | wx.ALL, border=1)
        button = wx.Button(self._panel, label="Stop")
        button.Bind(wx.EVT_BUTTON, self._on_stop_click)
        temp_sizer.Add(button, pos=(2, 1), flag=wx.ALIGN_CENTER | wx.ALL, border=1)

        box_sizer.Add(temp_sizer, flag=wx.EXPAND | wx.ALL, border=1)
        self._panel_sizer.Add(box_sizer, pos=(3, 0), span=(1, 4),
                              flag=wx.EXPAND | wx.ALL, border=6)

    def _init_canvas_block(self):
        self._canvas = CanvasPanel(self._panel)
        self._panel_sizer.Add(self._canvas, pos=(0, 4), span=(4, 1),
                              flag=wx.EXPAND | wx.TOP | wx.RIGHT | wx.BOTTOM, border=7)

    def _on_color_dialog_click(self, event):
        dialog = wx.ColourDialog(self)
        dialog.GetColourData().SetChooseFull(True)

        if dialog.ShowModal() == wx.ID_OK:
            data = dialog.GetColourData()
            button = event.GetEventObject()
            button.SetBackgroundColour(data.GetColour().Get())
        dialog.Destroy()

    def _change_emitter(self):
        x_coord = self._widgets['x_coord'].GetValue()
        y_coord = self._widgets['y_coord'].GetValue()
        u_direct = self._widgets['u_direct'].GetValue()
        v_direct = self._widgets['v_direct'].GetValue()
        self._emitter.change_properties([x_coord, y_coord], [u_direct, v_direct])

    def _on_emitter_change_click(self, event):
        self._change_emitter()

    def _on_random_particle_generation_click(self, event):
        self._clear()
        self._is_solar_mode = False
        widget = self._widgets['random_generation']
        value = widget.GetValue()
        self._emitter.generate_particles(value)
        self._max_coord = self._emitter.max_coord
        self._is_calculated = True

    def _on_single_particle_generation_click(self, event):
        if self._is_solar_mode:
            self._clear()
            self._is_solar_mode = False
        self._change_emitter()
        u_speed = self._widgets['u_speed'].GetValue()
        v_speed = self._widgets['v_speed'].GetValue()
        life_time = self._widgets['life_time'].GetValue()
        color = self._widgets['color'].GetBackgroundColour()
        mass = self._widgets['mass'].GetValue()
        self._emitter.create_particle(speed=[u_speed, v_speed], mass=mass,
                                      color=color, life_time=life_time)
        self._max_coord = self._emitter.max_coord
        self._is_calculated = True

    def _update_canvas(self, frame):
        if not self._is_calculated:
            return

        if not self._emitter.particles:
            self._canvas.clear()
            self._is_calculated = False
            return

        particles = self._emitter.particles
        marker_positions = [np.array(p.coordinates) / self._max_coord for p in particles]
        if self._is_solar_mode:
            marker_positions = [np.array(p) / 2.1 + 0.5 for p in marker_positions]
        marker_sizes = [p.radius for p in particles]
        marker_colors = [[c / 255 for c in p.color] for p in particles]
        self._canvas.draw_markers(marker_positions,
                                  marker_sizes, marker_colors)

        print(self._emitter)
        delta_t = 10 ** 6 if self._is_solar_mode else 1
        method_name = self._widgets['method'].GetValue()
        self._emitter.particles = calculate_particle_motion(particles, delta_t, method_name)

    def _on_loading_click(self, event):
        self._clear()
        file_name = 'solar_system.json'
        load_data(file_name, self._emitter)
        self._is_solar_mode = True

        coords = []
        for p in self._emitter.particles:
            coords.append(np.abs(p.coordinates))
        self._max_coord = np.max(coords)

        masses = dict(enumerate([p.mass for p in self._emitter.particles]))
        sorted_keys = sorted(masses, key=masses.get)
        sizes = np.linspace(50, 200, len(masses))
        for i in range(len(masses)):
            key = sorted_keys.index(i)
            self._emitter.particles[i].radius = sizes[key]

    def _clear(self):
        self._emitter.particles = []
        self._canvas.clear()

    def _on_clear_click(self, event):
        self._clear()

    def _on_start_click(self, event):
        self._is_calculated = True

    def _on_stop_click(self, event):
        self._is_calculated = False
