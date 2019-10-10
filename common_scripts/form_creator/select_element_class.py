# -*- coding: utf-8 -*-
from System.Windows.Forms import Label, AnchorStyles, BorderStyle, DockStyle
from System.Drawing import Color, Font, FontStyle, ContentAlignment
from common_scripts import *
from Autodesk.Revit.UI.Selection import ObjectType
from Autodesk.Revit.DB import ElementId
from Autodesk.Revit.Exceptions import OperationCanceledException

uidoc = __revit__.ActiveUIDocument


class MySelectElement:
    def __init__(self, panel, name, from_memory=None):
        self.name = name
        self.panel = panel
        if not from_memory:
            self.elem = None
            self.is_clicked = False
            self.button = self.panel.add_button('Выбрать элемент')
        else:
            self.elem = ElementId(from_memory)
            self.is_clicked = True
            self.button = self.panel.add_button('Выбрать другой элемент')
            self.label = self.panel.add_label('')
            self.label.Text = 'Выбран элемент = ' + to_str(self.elem)
        self.button.BackColor = Color.Green
        self.button.Click += self.select_element

    def select_element(self, sender, args):
        try:
            if not self.is_clicked:
                self.label = self.panel.add_label('Выбран элемент')
                self.is_clicked = True
            ref = uidoc.Selection.PickObject(ObjectType.Element)
            self.elem = uidoc.Document.GetElement(ref).Id
            self.label.Text = 'Выбран элемент = ' + to_str(self.elem)
            self.button.Text = 'Выбрать другой элемент'
        except OperationCanceledException:
            pass
        self.panel.Parent.Activate()

    def GetValue(self):
        if self.elem:
            return self.elem
