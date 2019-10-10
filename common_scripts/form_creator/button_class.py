# -*- coding: utf-8 -*-
from System.Windows.Forms import Button, AnchorStyles, BorderStyle, DockStyle
from System.Drawing import Color, Font, FontStyle

class MyButton(Button):
    def __init__(self, name, type_of_button, panel):
        self.Text = name
        self.BackColor = Color.Brown
        self.AutoSize = True
        self.BorderStyle = BorderStyle.FixedSingle
        self.ForeColor = Color.White
        self.Dock = DockStyle.Top
        self.Height = 25
        self.panel = panel

        if type_of_button == 'success':
            pass

    def AddFunction(self, func, *arg):
        self.Click += self.func_wrapper(func, *arg)

    def func_wrapper(self, func, *arg):
        def wrapped(hand, e):
            func(*arg)
        return wrapped
