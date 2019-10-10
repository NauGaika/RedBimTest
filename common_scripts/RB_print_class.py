# -*- coding: utf-8 -*-
from System.Windows.Forms import MessageBox, Application, Form, DockStyle, BorderStyle, TextBox, ScrollBars
from System.Drawing import Font
from common_scripts import *

class Printer(Form):
    def __init__(self, RB_print):
        self.RB_print = RB_print
        self.Text = 'RedBim'
        self.Name = 'RedBimPrinter'
        self.Height = 500
        self.Width = 700
        self.label = TextBox()
        self.label.Dock = DockStyle.Fill
        self.label.Multiline = True
        self.label.ReadOnly = True
        self.label.Font = Font('Arial', 12)
        self.label.ScrollBars = ScrollBars.Vertical
        self.Controls.Add(self.label)

    def echo(self, str):
        self.label.Text += '\n\r' + str
        self.Activate()

class RB_print:
    def __init__(self):
        self.is_show = False

    def Show(self, str):
        if not self.is_show:
            self.create_form()
        self.form.echo(str)
        #MessageBox.Show(str, 'RedBim')
        self.is_show = True

    def create_form(self):
        self.form = Printer(self)
        self.form.Show()

    def Close(self):
        self.form.Close()
