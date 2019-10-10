# -*- coding: utf-8 -*-
from System.Windows.Forms import Application, Form, DockStyle, BorderStyle
from System.Drawing import Color
from common_scripts.form_creator.panel_class import MyPanel
from common_scripts import *

class Form_creator(Form):
    name = ""
    count = 0
    lines = None
    max_scrin = 1024

    def __init__(self):
        pass
    #Начинает работу с формами
    def Start(self, lines, memory=None):
        self.MEMORY = memory
        self.__class__.count += 1
        self.Name = 'form_' + str(self.__class__.count)
        self.Text = 'RedBim'
        self.lines = []
        self.create_lines(lines)
        self.BackColor = Color.Gray
        self.Width = 700
        
    #Создает форму на экране
    def Create(self, exEvent):
        self.calculate_size()
        self.exEvent = exEvent
        if self.MEMORY:
            self.Closed += self.Save
        self.Show()

    #Вычисляет размеры формы
    def calculate_size(self):
        self.Height = 0
        for i in self.lines:
            self.Height += i.Height
        if self.Height > self.max_scrin:
            self.Height = self.max_scrin
            self.AutoScroll = True

    #Получает линию
    def GetLines(self, number):
        return self.lines[len(self.lines) - number]

    #Создает панели в виде линий в форме по заданному количеству
    def create_lines(self, count = 2):
        for i in range(0, count):
            color = Color.Gray
            if i%2>0:
                color = Color.DarkGray
            panel = MyPanel(color)
            self.lines.append(panel)
            self.Controls.Add(panel)
    #Сохраняем в память все данные
    def Save(self, hand, e):
        for i in MyPanel.all_controller:
            self.MEMORY.SetAttr(i.name, i.GetValue())
        self.MEMORY.Close()
