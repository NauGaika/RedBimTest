# -*- coding: utf-8 -*-
from .Panel import Precast_panel
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, FamilyInstance


class Precast_finder(object):
    "Поиск элементов относящихся к сборняку."
    panel_prefix = "215"
    panel_parametrical_prefix = "214"

    @property
    def panels(self):
        "Поиск панелей."
        if not hasattr(self, "_panels"):
            self._panels = []
            if not self.uidoc.Selection.GetElementIds().Count:
                wall_panels = FilteredElementCollector(self.doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()
            else:
                wall_panels = [self.doc.GetElement(i) for i in self.uidoc.Selection.GetElementIds()]
            for i in wall_panels:
                if isinstance(i, FamilyInstance):
                    geometrical = i.Symbol.Family.Name[:len(self.panel_prefix)] == self.panel_prefix
                    parametrical = i.Symbol.Family.Name[:len(self.panel_parametrical_prefix)] == self.panel_parametrical_prefix
                    if geometrical or parametrical:
                        self._panels.append(Precast_panel(i, doc=self.doc, analys_geometry=self.analys_geometry, geometrical=geometrical))
        return self._panels
