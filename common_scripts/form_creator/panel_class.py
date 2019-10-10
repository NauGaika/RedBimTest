# -*- coding: utf-8 -*-
from System.Windows.Forms import Panel, DockStyle, BorderStyle, Button, AnchorStyles
from System.Drawing import Color
from common_scripts.form_creator.button_class import MyButton
from common_scripts.form_creator.label_class import MyLabel
from common_scripts.form_creator.checked_list_box_class import MyCheckedListBox
from common_scripts.form_creator.text_box_class import MyTextBox
from common_scripts.form_creator.select_element_class import MySelectElement

from common_scripts import *

class MyPanel(Panel):
    all_elem = None
    all_controller = []
    def __init__(self, color = Color.DarkGray):
        self.all_elem = []
        self.Dock = DockStyle.Top
        self.AutoSize = True
        self.BorderStyle = BorderStyle.FixedSingle
        self.BackColor = color


    def add_button(self, name, type_of_button = 'success'):
        button = MyButton(name, type_of_button, self)
        self.Controls.Add(button)
        return button

    def add_label(self, text):
        label = MyLabel(text, self)
        self.Controls.Add(label)
        return label
    #Добавляет текстовое поле
    def add_textbox(self, name, text, MEMORY=None):
        textbox = None
        if MEMORY and MEMORY.GetAttr(name):
            textbox = MyTextBox(MEMORY.GetAttr(name), self, name)
        else:
            textbox = MyTextBox(text, self, name)
        self.Controls.Add(textbox)
        self.__class__.all_controller.append(textbox)
        return textbox
    #Добавляет список с чекбоксами
    def add_checked_list_box(self, name, array, MEMORY=None):
        elem = None
        if MEMORY and MEMORY.GetAttr(name):
            elem = MyCheckedListBox(self, name, MEMORY.GetAttr(name))
        else:
            elem = MyCheckedListBox(self, name, array)
        self.Controls.Add(elem)
        self.__class__.all_controller.append(elem)
        return elem
    #Выбираем элемент
    def add_select_element(self, name, MEMORY=None):
        select = None
        if MEMORY and MEMORY.GetAttr(name) and MEMORY.GetAttr(name) != 'None':
            select = MySelectElement(self, name, int(MEMORY.GetAttr(name)))
        else:
            select = MySelectElement(self, name)
        self.__class__.all_controller.append(select)
        return select
