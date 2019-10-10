# -*- coding: utf-8 -*-
"""Класс по созданию PushButton."""

import os
import re
from constants import START_SCRIPT, STATIC_IMAGE  # Константы
from System import Uri
from common_scripts import echo, to_str
from PyPushButtonData import PyPushButtonData
from System.Windows.Media.Imaging import BitmapImage


class RB_Pushbutton:
    """Класс по созданию PushButton."""

    PB_count = 0

    def __init__(self, direct, parent, is_user=False):
        """Инициализируем direct, parent, is_user."""
        self.is_user = is_user
        self.path = direct
        self.parent = parent
        echo("Начинаем создание кнопки " + self.name)
        panel = self.parent.sys_panel
        if panel:
            self.__class__.PB_count = self.__class__.PB_count + 1
            self.get_button_or_create()
            self.add_image()

    def get_button_or_create(self):
        """Существует ли кнопка. Если да - вернем ее."""
        echo("Существует ли кнопка " + self.name)
        self.button = self.pushbutton_is_exist()
        if not self.button:
            echo("Нет")
            self.button = self.parent.sys_panel.AddItem(self.create_PPBD())
        else:
            echo("Да")

    def create_PPBD(self):
        """Создает экземпляр PPBD."""
        echo("Создаем экземпляр PPBD " + self.name)
        echo("Путь " + self.script_path)
        return PyPushButtonData(
                self.name + str(self.PB_count),
                self.name + str(self.PB_count),
                self.script_path,
                __revit__,
                START_SCRIPT
            ).Finish()

    def pushbutton_is_exist(self):
        """Проверяет на существование кнопки по имени."""
        for pb in self.parent.sys_panel.GetItems():
            if pb.Name == self.name:
                return pb

    @property
    def name(self):
        """Получает имя pushbutton."""
        name = ""
        if not self.is_user:
            pattern = r'[0-9A-Za-zА-Яа-яёЁ_ -]+\.pushbutton$'
            result = re.search(pattern, self.path)
            line = result.group(0)
            name = line.split('.')[0]
        return name

    def add_image(self):
        """Добавляем картинку."""
        self.img_uri = Uri(self.image)
        self.button.LargeImage = BitmapImage(self.img_uri)
        self.button.Image = BitmapImage()
        self.button.Image.BeginInit()
        self.button.Image.UriSource = self.img_uri
        self.button.Image.DecodePixelHeight = 16
        self.button.Image.DecodePixelWidth = 16
        self.button.Image.EndInit()

    @property
    def script_path(self):
        """Получаем путь к скрипуту __init__.py."""
        script_path = None
        if not self.is_user:
            files = os.listdir(self.path)
            for i in files:
                if os.path.isfile(os.path.join(self.path, i)):
                    line = to_str(i)
                    if line == '__init__.py':
                        script_path = os.path.join(self.path, i)
        else:
            script_path = self.path
        return script_path

    @property
    def image(self):
        """Картинка данной кнопки."""
        return os.path.join(STATIC_IMAGE, 'standart_lage_image.png')
