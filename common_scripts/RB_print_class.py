# -*- coding: utf-8 -*-
from System.Windows.Forms import MessageBox, Application, Form, DockStyle, BorderStyle, TextBox, ScrollBars, AnchorStyles, AutoScaleMode
from System.Windows.Forms import ImageLayout, FormStartPosition, Label
from System.Drawing import Font, FontStyle, Color, Point, Image, Icon
from System import Uri
from System.Windows.Forms import Clipboard
# from System.Windows.Media.Imaging import BitmapImage
# from common_scripts import *
# from RedBimEngine.constants import STATIC_IMAGE
# from RedBimEngine.constants import START_SCRIPT, STATIC_IMAGE
import os.path
STATIC_IMAGE = __file__
prev_path = ""
while "RedBim" not in prev_path:
    STATIC_IMAGE = os.path.abspath(os.path.dirname(STATIC_IMAGE))
    prev_path = os.path.split(STATIC_IMAGE)[-1]
STATIC_IMAGE = os.path.join(STATIC_IMAGE, 'static\\img')

class Printer(Form):
    def __init__(self, RB_print):
        self.RB_print = RB_print
        self.Text = 'RedBim'
        self.Name = 'RedBimPrinter'
        self.Height = 500
        self.Width = 700
        self.AutoScroll = True
        self.AutoScaleMode = AutoScaleMode.Font
        self.BackColor = Color.FromArgb(67, 67, 67)
        # self.BackgroundImage = Image.FromFile(os.path.join(STATIC_IMAGE, "bg.png"))
        # self.BackgroundImageLayout = ImageLayout.Center
        self.Icon = Icon(os.path.join(STATIC_IMAGE, "icon.ico"), 16, 16)
        self.StartPosition = FormStartPosition.CenterScreen;

        self.label = Label()
        self.label.Anchor = (AnchorStyles.Top|AnchorStyles.Left|AnchorStyles.Right)
        self.label.BackColor = Color.FromArgb(0,0,0,0)
        self.label.Font = Font("ISOCPEUR", 12, FontStyle.Italic)
        self.label.ForeColor = Color.White
        self.label.Location = Point(0,0)
        self.label.Name = "text"
        self.label.Dock = DockStyle.Top
        self.label.AutoSize = True
        self.Controls.Add(self.label)
        self.label.Click += self.add_to_clipboard

    def add_to_clipboard(self, v, arr):
        Clipboard.SetText(self.label.Text)
        message("Лог скопирован в буфер обмена.")

    def echo(self, str):
        self.label.Text = self.label.Text + "\r\n" + str
        # self.ScrollToCaret()
        self.label.Update()
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

def message(text):
    MessageBox.Show(text, 'RedBim')