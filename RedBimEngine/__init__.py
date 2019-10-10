# -*- coding: utf-8 -*-

 # Поиск вкладок
"""Здесь начинается запуск движка."""

import clr
import sys
import os
from constants import HOME_DIR  # Подгружаю константы
clr.AddReference('System')
clr.AddReference('PresentationCore')
clr.AddReference('System.Windows')
clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Drawing')
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
clr.AddReference('AdWindows')
clr.AddReference("UiFramework")


# Добавляю загрузчику папку
sys.path.append(
    '\\\\picompany.ru\\pikp\\Dep\\LKP4\\WORK\\scripts\\loader')
clr.AddReferenceToFileAndPath('PyPushButtonData')
from Tab_finder import find_all_tab

__all__ = ['find_all_tab']
# rb_all_tabs = find_all_tab()  # Запускаем поиск влкдок
