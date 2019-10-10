# -*- coding: utf-8 -*-
"""Класс по созданию вкладок Revit."""

import os
import re
import Autodesk.Windows as AdWin
from constants import DIR_SCRIPTS, LOGO, USERNAME  # Подгружаем общие перемен
from common_scripts import echo, to_str
from RB_Panel_class import RB_Panel  # Подгружаем класс панелей


class RB_Tab:
    """Класс по созданию вкладок."""

    path = ''
    panels = []
    sys_tab = None

    def __init__(self, direct, script_path, is_user=False):
        """Инициализируем наш объект. Передать direct, is_user."""
        self.is_user = is_user
        self.panels = []
        self.sys_tab = None
        self.path = os.path.join(script_path, direct)
        echo("Создаем вкладку " + self.name)
        self.tab_is_create = False
        try:
            if not self.tab_is_exist():
                self.sys_tab = self.create_tab()
        except Exception:
            echo("Ошибка при создании вкладки " + self.name)
        echo("Ищем панели в " + self.name)
        self.find_panel()

    def tab_is_exist(self):
        """Вкладка уже существует?."""
        addWinRibbon = AdWin.ComponentManager.Ribbon
        if addWinRibbon.FindTab(self.name):
            echo('Вкладка ' + self.name + ' существует')
            return True

    def remove_tab(self):
        """Удаляем вкладку по имени."""
        addWinRibbon = AdWin.ComponentManager.Ribbon
        tab = addWinRibbon.FindTab(self.name)
        addWinRibbon.Tabs.Remove(tab)

    #
    def create_user_panel(self):
        """Создаем пользовательскую вкладку."""
        self.panels.append(RB_Panel(
            to_str(os.path.join(self.path)),
            self,
            True)
            )

    @property
    def name(self):
        """Получаем имя вкладки."""
        name = ""
        if not self.is_user:
            pattern = r'[0-9A-Za-zА-Яа-яёЁ_ -]+\.tab$'
            result = re.search(pattern, self.path)
            line = result.group(0)
            name = line.split('.')[0]
            name = LOGO + ':' + name
        else:
            name = LOGO + ':' + USERNAME
        return name

    def create_tab(self):
        """Создаем вкладку."""
        tab = __revit__.CreateRibbonTab(self.name)
        echo("Вкладка" + self.name + " создана")
        return tab

    def find_panel(self):
        """Ищем панели в данной вкладке."""
        files = os.listdir(self.path)
        for i in files:
            if os.path.isdir(os.path.join(self.path, i)):
                line = i
                pattern = r'panel$'
                result = re.search(pattern, line)
                if result:
                    panel_path = os.path.join(self.path, i)
                    echo("Создаем панель по пути " + panel_path)
                    new_panel = RB_Panel(panel_path, self)
                    self.panels.append(new_panel)
