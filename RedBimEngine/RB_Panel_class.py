# -*- coding: utf-8 -*-
"""Здесь находится класс RB_Panel по созданию панелей.

Используется в RB_Tab_class
"""

import os
import re
import Autodesk.Windows as AdWin
import UIFramework
from constants import USERNAME, LOGO   # Подгружаем общие переменные
from common_scripts import echo
from RB_Pushbutton_class import RB_Pushbutton  # Подгружаем класс кнопок


class RB_Panel:
    """Класс по созданию панелей. Используется в RB_Tab_class."""

    def __init__(self, direct, parent, is_user=False):
        """direct, parent, is_user."""
        echo('***********************')
        self.is_user = is_user
        self.pushbutton = []  # Все кнопки в панели depricated
        self.path = direct
        self.parent = parent
        self.sys_panel = self.create_panel()  # Ревитовский объект с панелью
        self.controls = self.control_finder()  # Все кнопки в панели

    @property
    def rev_panel(self):
        """Находит ревитовскую панель и возвращает ее"""
        echo(self.parent.name)
        for panel in __revit__.GetRibbonPanels(self.parent.name):
            echo(panel)
            if panel.Title == self.name:
                return panel
    @property
    def name(self):
        """Получает имя панели."""
        name = ""
        if not self.is_user:
            line = os.path.split(self.path)[1]
            name = line.split('.')[0]
        else:
            name = LOGO + ':' + USERNAME
        return name

    @property
    def panel_is_exist(self):
        """Проверяет наличие панели в данной вкладке."""
        echo("Панель " + self.name + " уже есть во вкладке "
             + self.parent.name + " ?")
        print(self.parent.name)
        for panel in __revit__.GetRibbonPanels(self.parent.name):
            if panel.Name == self.name:
                echo("да")
                return panel
        echo("нет")
        return False

    def create_panel(self):
        """Создаем ревитовскую панель и сохраняем ее в sys_tab."""
        nrp = self.panel_is_exist
        if not nrp:
            echo("Пытаемся создать панель " + self.name)
            nrp = __revit__.CreateRibbonPanel(self.parent.name, self.name)
        return nrp

        echo("Панель " + self.name + " существует")

    def control_finder(self):
        """Ищет все кнопки в нужной папке."""
        controls = []
        files = os.listdir(self.path)
        for file in files:
            controls.append(self.type_of_item(file))
        return controls

    def type_of_item(self, name):
        """Возвращает класс по имени файла."""
        if re.search(r'pushbutton$', name):
            return RB_Pushbutton(os.path.join(self.path, name), self)

    # def pushbutton_finder(self):
    #     """Ищет кнопки по пути."""
    #     files = os.listdir(self.path)
    #     for i in files:
    #         if not self.is_user:
    #             if os.path.isdir(os.path.join(self.path, i)):
    #                 line = i
    #                 pattern = r'pushbutton$'
    #                 result = re.search(pattern, line)
    #                 if result:
    #                     self.pushbutton.append(
    #                         RB_Pushbutton(os.path.join(self.path, i), self)
    #                         )
    #         else:
    #             if os.path.isfile(os.path.join(self.path, i)):
    #                 line = i
    #                 pattern = r'\.py$'
    #                 result = re.search(pattern, line)
    #                 if result:
    #                     self.pushbutton.append(
    #                         RB_Pushbutton(
    #                             os.path.join(self.path, i),
    #                             self,
    #                             True)
    #                         )
