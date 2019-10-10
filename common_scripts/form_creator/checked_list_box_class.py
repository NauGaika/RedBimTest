# -*- coding: utf-8 -*-
from System.Windows.Forms import CheckedListBox, AnchorStyles, BorderStyle, DockStyle
from System.Drawing import Color, Font, FontStyle, ContentAlignment
from common_scripts import *
from System import Array

class MyCheckedListBox(CheckedListBox):
    def __init__ (self, panel, name,  arr=[]):
        self.name = name
        self.panel = panel
        self.Dock = DockStyle.Top
        self.MultiColumn  = True
        for i in arr:
            if (type(i) is tuple) or type(i) is list:
                self.Items.Add(i[0], i[1])
            else:
                self.Items.Add(i)
        self.Height = 240

    def set_value_checked(self, name, val):
        count = 0
        numb = 'not found'
        for i in self.Items:
            count += 1
            if name == i:
                numb = count
        self.SetItemChecked(numb-1, val)

    def GetValue(self):
        new_dict = {}
        count = 0
        for i in self.Items:
            new_dict.update({i: self.GetItemChecked(count)})
            count += 1
        return new_dict
