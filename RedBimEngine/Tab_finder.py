# -*- coding: utf-8 -*-
"""Модуль который ищет вкладки. Здесь функция find_all_tab."""

import os
import re

from constants import DIR_SCRIPTS, DIR_SYSTEM_SCRIPTS  # Подгружаем общие переменные
from common_scripts import echo
from RB_Tab_class import RB_Tab  # Подгружаем класс с вкладками


def find_all_tab(developer=False):
    """Находит все вкладки в script_path."""
    all_tab = []
    script_path = DIR_SCRIPTS
    echo("Получаем имена всех вкладок с  " + script_path)
    files = os.listdir(script_path)
    echo(files)
    echo("____________________", "Создаем все вкладки")
    echo('\n')
    for file in files:
        os.path.isdir(os.path.join(script_path, file))
        is_tab = re.search(r".tab$", file)
        if is_tab:
            if  (not developer and "test.tab" not in file) or developer:
                all_tab.append(RB_Tab(file, script_path))
        echo('\n')
    if not all_tab:
        echo("Папок со скриптами нет")
    return all_tab


__all__ = ['find_all_tab']
