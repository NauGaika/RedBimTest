# -*- coding: utf-8 -*-
from .Panel import Precast_panel
from common_scripts import echo
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, FamilyInstance
from Autodesk.Revit.DB import AssemblyInstance


class Precast_finder(object):
    "Поиск элементов относящихся к сборняку."
    panel_prefix = "215"
    panel_prefix_container = "216"
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
        Должен быть префикс 215
        216 префикс у контейнеров

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
            sel_id = self.uidoc.Selection.GetElementIds()
            if not sel_id.Count:
                wall_panels = FilteredElementCollector(self.doc).OfCategory(
                    BuiltInCategory.OST_Walls).WhereElementIsElementType()
                wall_panels.UnionWith(FilteredElementCollector(
                    self.doc).OfCategory(BuiltInCategory.OST_Columns).WhereElementIsNotElementType())
                wall_panels = wall_panels.ToElements()
            else:
                sel_elements = [self.doc.GetElement(
                    i) for i in self.uidoc.Selection.GetElementIds()]
                wall_panels = []
                for i in sel_elements:
                    if isinstance(i, AssemblyInstance):
                        wall_panels += [self.doc.GetElement(j) for j in i.GetMemberIds()]
                    else:
                        wall_panels.append(i)
                        wall_panels += [self.doc.GetElement(k) for j in wall_panels for k in j.GetSubComponentIds()]
            for i in wall_panels:
                if isinstance(i, FamilyInstance):
                    geometrical = i.Symbol.Family.Name[:len(
                        self.panel_prefix)] == self.panel_prefix

                    parametrical = i.Symbol.Family.Name[:len(
                        self.panel_parametrical_prefix)] == self.panel_parametrical_prefix
                    if geometrical or parametrical:
                        self._panels.append(Precast_panel(
                            i, doc=self.doc, analys_geometry=self.analys_geometry, geometrical=geometrical))
        return self._panels
