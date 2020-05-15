# -*- coding: utf-8 -*-
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, ViewSheet
from Autodesk.Revit.DB import ScheduleFieldType


class Scheduled_Complexity:
    "Спецификации."

    def __init__(self, doc, element, parent=None):
        self.doc = doc
        self.element= element
        self.definition = self.element.Definition
        self.parent = parent
        self.childs = []
        if self.parent:
            self.parent.childs.append(self)
        self.define_scheduled_fields()

    def define_scheduled_fields(self):
        self._all_scheduled_fileds = [self.definition.GetField(i) for i in self.definition.GetFieldOrder()]
        if not hasattr(self, "_scheduled_fileds_formula"):
             self._scheduled_fileds_formula = 0
        if not hasattr(self, "_scheduled_fileds_else"):
            self._scheduled_fileds_else = 0

        for i in self._all_scheduled_fileds:
            if i.FieldType == ScheduleFieldType.Formula:
                self._scheduled_fileds_formula += 1
            else:
                self._scheduled_fileds_else += 1

    @property
    def scheduled_groups(self):
        if not hasattr(self, "_scheduled_groups"):
            self._scheduled_groups = self.definition.GetSortGroupFields().Count
        return self._scheduled_groups
    

    @property
    def obj(self):
        res = {
            "element_id": str(self.element.Id.IntegerValue),
            "element_name": self.element.Title,
            "scheduled_fileds_formula": self._scheduled_fileds_formula,
            "scheduled_groups": self.scheduled_groups,
            "scheduled_fileds_else": self._scheduled_fileds_else
        }
        for i in self.childs:
            for key, value in i.obj.items():
                if key == "element_id" or key == "element_name":
                    continue 
                res.setdefault(key, 0)
                res[key] += value
        return res
    