# -*- coding: utf-8 -*-
from .Panel import Precast_panel
from common_scripts import echo
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, FamilyInstance


class Precast_finder(object):
    "Поиск элементов относящихся к сборняку."
    panel_prefix = "215"
    panel_prefix_2 = "216"
    panel_parametrical_prefix = "214"

    @property
    def panels(self):
        """
        Поиск панелей.

        Если выбран элемент.
        Выбираем у него все, что вложено

        Если не выбран - берем все элементы категории стены и колонны.

        Проходим по всем элементам.
        Если является эеземпляром семейства, не системное.
        Идем дальше.
        Проверяем является ли семейство геометрическое:
        Должен быть префикс 215 или 216

        Проверяем является ли семейство параметрическим.
        Префикс 214

        Если семейство геометрическое, либо параметрическое, добавляем
        в _panels экземпляр класса Precast_panel.
        с параметром geometrical говорящее. является ли элемент
        геометрическим.

        Так же прокидываем нужно ли анализировать геометрию.
        Если нет - будет выполнено только объединение и заполнение параметров.
        См. класс Precast_panel
        """
        if not hasattr(self, "_panels"):
            self._panels = []
            if not self.uidoc.Selection.GetElementIds().Count:
                wall_panels = FilteredElementCollector(self.doc).OfCategory(
                    BuiltInCategory.OST_Walls).WhereElementIsNotElementType()
                wall_panels = wall_panels.UnitonWith(FilteredElementCollector(
                    self.doc).OfCategory(BuiltInCategory.OST_Columns).WhereElementIsNotElementType())
                wall_panels = wall_panels.ToElements()
            else:
                wall_panels = [self.doc.GetElement(
                    i) for i in self.uidoc.Selection.GetElementIds()]
                sub_walls = [self.doc.GetElement(
                    i) for j in wall_panels for i in j.GetSubComponentIds()]
                wall_panels = list(wall_panels) + list(sub_walls)
            for i in wall_panels:
                if isinstance(i, FamilyInstance):
                    geometrical = i.Symbol.Family.Name[:len(
                        self.panel_prefix)] == self.panel_prefix
                    geometrical = geometrical or (i.Symbol.Family.Name[:len(
                        self.panel_parametrical_prefix)] == self.panel_prefix_2)
                    parametrical = i.Symbol.Family.Name[:len(
                        self.panel_parametrical_prefix)] == self.panel_parametrical_prefix
                    if geometrical or parametrical:
                        self._panels.append(Precast_panel(
                            i, doc=self.doc, analys_geometry=self.analys_geometry, geometrical=geometrical))
        return self._panels
