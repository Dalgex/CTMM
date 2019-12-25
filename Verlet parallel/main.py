import wx
from form import Form

if __name__ == "__main__":
    app = wx.App()
    form = Form(parent=None, id=-1, title="Particle system")
    app.SetTopWindow(form)
    app.MainLoop()
