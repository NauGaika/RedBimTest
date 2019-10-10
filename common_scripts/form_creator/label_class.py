# -*- coding: utf-8 -*-
from System.Windows.Forms import Label, AnchorStyles, BorderStyle, DockStyle
from System.Drawing import Color, Font, FontStyle, ContentAlignment

class MyLabel(Label):
    def __init__(self, text, parent):
        self.Text = text
        self.Width = parent.Width
        self.ForeColor = Color.White
        self.TextAlign = ContentAlignment.MiddleCenter
        self.Dock = DockStyle.Top
