# -*- coding: utf-8 -*-
from .Precast_finder import Precast_finder
from common_scripts.line_print import Line_printer
import json
from common_scripts import echo
import clr
import re
import os.path as path
import httplib
import urllib
import sys
cur_path = path.split(__file__)[0]


class Precast(Precast_finder):
    "Класс отвечающий за сборные конструкции."

    URI = 'vpp-map01'
    panel_server_path = "/v1/Panel/"

    def __init__(self, __revit__, analys_geometry=True, create_new_panel=False, old_format_path=None, set_parameters=True):
        "Создаем объект на основе документа проекта."
        self.uidoc = __revit__.ActiveUIDocument
        self.doc = self.uidoc.Document
        self.analys_geometry = analys_geometry
        self.create_new_panel = create_new_panel
        self.old_format_path = old_format_path
        self.all_panels = True  # Выбирать ли 214 панели или нет
        self.set_parameters = set_parameters

    def define_section(self):
        """
            Определение геоетрии для кнопки по передаче в базу.

            1. Получить панели
            Получаем с помощью self.panels из Precast_finder
            2. Проанализировать геометрию
            Анализируется в конструкторе панели при создании см. Precast_finder
            3. Создать JSON на основе panel.json
            4. Отправить JSON в базу и получить результат
            5. Проанализировать полученный JSON От базы
            6. Присвоить панели BDS_SystemTag BDS_AdvanceTag и BDS_Tag
        """
        template_for_mark = re.compile("-\[.*\]-")
        action_type = "find" if not self.create_new_panel else "findOrCreate"

        all_json = []
        for i in self.panels:
            i.set_mass_parameter()
            i.set_volume_parameter()
            i.join_units_to_panel()
            if i.is_analysed:
                js = i.json
                if i.is_valid:
                    all_json.append(js)
                    i.element.LookupParameter("JSON").Set(json.dumps(i.json))
                else:
                    echo("Ошибка в валидации панели {}".format(i))
                    i.status = "3"

        # Отправляем запрос на сервер с панелями
        result_str = self.find_panels_on_server(
            all_json, action_type=action_type)
        # Смотрим, что вернул сервер
        result = json.loads(result_str)
        if isinstance(result, list):
            # Вернулся массив
            for i in result:
                # Итерируемся по всем, что есть в массивие
                for j in self.panels:
                    # Находим каждую панельку по handle в нем id панели в ревит
                    if int(i["value"]["handle"]) == j.Id:
                        if i["status"] == "Created":
                            # Вернулся статус что панелька новая и она создана.
                            # Если action_type=findOrCreate
                            j.advance_tag = i["value"]["mark"]
                            if action_type == "find":
                                echo("Назначена предварительная марка {} элементу {}".format(
                                    i["value"]["mark"], j.Id))
                                j.advance_tag = i["value"]["mark"]
                                j.system_tag = ""
                                j.tag = template_for_mark.split(
                                    i["value"]["mark"])[1] + "(prev)"
                                j.status = "2"
                            else:
                                j.system_tag = i["value"]["mark"]
                                j.tag = template_for_mark.split(
                                    i["value"]["mark"])[1]
                                j.advance_tag = ""
                                j.status = "4"
                                echo("Создана панель с маркой {} для элемента {}".format(
                                    i["value"]["mark"], j.Id))
                        else:
                            j.system_tag = i["value"]["mark"]
                            j.tag = template_for_mark.split(
                                i["value"]["mark"])[1]
                            j.advance_tag = ""
                            j.status = "1"
                            echo("Найдена существующая панель с маркой {} для элемента {}".format(
                                i["value"]["mark"], j.Id))
                        # Для каждой вернувшейся панели создаем old_format. Для этого передаем вернувшиеся данные панели.
                        if self.old_format_path:
                            j.make_old_format(i, self.old_format_path)
        else:
            echo("Вернулся не массив ", result_str)

    def find_panels_on_server(self, parameters=None, action_type="find"):
        """
        Метод отправляет запрос на сервер для поиска панелей.
        Возвращает строку с панелями. 

        Передавать нужно parameters - массив
        action_type - действие, которое нуно выполнить
        """
        parameters = json.dumps(parameters).replace('"', '\"')
        headers = {
            "Content-type": "application/json",
            "Accept": "application/json"
        }
        conn = httplib.HTTPConnection(self.URI)
        conn.request("POST", self.panel_server_path +
                     action_type, parameters, headers)
        response = conn.getresponse()
        return response.read().decode("utf-8")

    def join_unit_to_panels(self):
        """Объединение узлов с панелями.

        Так же находит панельки, но при создании Precast не нужно
        анализировать геометрию. Т.к. происходит только объеднинение
        """
        self.all_panels = True
        for i in self.panels:
            i.join_units_to_panel()

    def set_mass(self):
        "Устанавливаем значение массы каждой панели."
        for i in self.panels:
            i.set_mass_parameter()

    def set_volume(self):
        "Устанавливаем значение объема каждой панели."
        for i in self.panels:
            i.set_volume_parameter()

    def set_window_to_panels(self):
        "Заполняет параметр Hole для панели."
        for i in self.panels:
            i.set_windows_to_panel()
