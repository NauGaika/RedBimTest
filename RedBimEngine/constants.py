# -*- coding: utf-8 -*-
"""Хранятся константы.

USERNAME
HOME_DIR
DIR_SCRIPTS
STATIC_IMAGE
USER_SCRIPTS
LOGO
"""
import os


def get_username():
    """Получить текущее имя пользователя."""
    uname = __revit__.Application.Username
    uname = uname.split('@')[0]
    uname = uname.replace('.', '')
    return uname


def parent_dir(dir, count=1):
    """Получает родительску дирректорию."""
    dir_name = dir
    while count:
        count -= 1
        dir_name = os.path.dirname(dir_name)
        dir_name = os.path.abspath(dir_name)
    return dir_name


USERNAME = get_username()
HOME_DIR = 'L:\\09_Программы\\RedBim'
LOADER = os.path.join(HOME_DIR, 'loader')
GOOGLE = os.path.join(LOADER, 'Google')
DIR_SCRIPTS = os.path.join(HOME_DIR, 'scripts')
DIR_SYSTEM_SCRIPTS = os.path.join(HOME_DIR, 'systemscripts')
STATIC_IMAGE = os.path.join(HOME_DIR, 'static\\img')
USER_SCRIPTS = os.path.join(HOME_DIR, 'scripts\\Пользовательские.tab\\Скрипты.panel')
USER_SCRIPT_TEMP = os.path.join(HOME_DIR, 'scripts\\Пользовательские.tab\\Временный.panel\\Временный.pushbutton\\__init__.py')
LOGO = 'RB'
START_SCRIPT = os.path.join(HOME_DIR, 'common_scripts\\start_of_script.py')

__all__ = ['USERNAME', 'HOME_DIR', 'DIR_SCRIPTS', 'STATIC_IMAGE',
           'USER_SCRIPTS', 'LOGO', 'START_SCRIPT', 'USER_SCRIPT_TEMP',
           'LOADER', 'GOOGLE']
