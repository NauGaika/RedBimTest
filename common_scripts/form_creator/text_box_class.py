# coding: utf8
from System.Windows.Forms import TextBox, AnchorStyles, BorderStyle, DockStyle, Keys
from System.Drawing import Color, Font, FontStyle, ContentAlignment
from common_scripts import *

class MyTextBox(TextBox):
    def __init__(self, text, panel, name, row=5):
        self.name = name
        self.panel = panel
        self.Text = text
        self.Dock = DockStyle.Top
        self.Height = row*18
        self.Multiline = True
        self.AutoSize = False

    def GetValue(self):
        return self.Text
        
    def AddFunction(self, func, *arg, **kwargs):
        keycode = None
        if 'keycode' in kwargs.keys():
            keycode = kwargs['keycode']
        if keycode is None:
            self.TextChanged += self.func_wrapper(func, *arg)
        else:
            self.KeyDown += self.func_wrapper(func, *arg, keycode=keycode)

    def func_wrapper(self, func, *arg, **kwargs):
        keycode = None
        if 'keycode' in kwargs.keys():
            keycode = kwargs['keycode']
        def wrapped(hand, e):
            if keycode is not None:
                if e.KeyCode==Keys.Return:
                    func(*arg)
            else:
                func(*arg)
        return wrapped