# coding: utf8
from System.Windows.Forms import TextBox, AnchorStyles, BorderStyle, DockStyle
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
        
    def AddFunction(self, func, *arg):
        self.TextChanged += self.func_wrapper(func, *arg)

    def func_wrapper(self, func, *arg):
        def wrapped(hand, e):
            func(*arg)
        return wrapped