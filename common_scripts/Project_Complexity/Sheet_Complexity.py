# -*- coding: utf-8 -*-
from Autodesk.Revit.DB import FilteredElementCollector, Viewport
from Autodesk.Revit.DB import TextNote, ScheduleSheetInstance


class Sheet_Complexity:
    all_view = set()
    def __init__(self, doc, element, parent=None):
        self.doc = doc
        self.element = element
        self.parent = parent
        self.childs = []
        if self.parent:
            self.parent.childs.append(self)

    @property
    def text_notes(self):
        if not hasattr(self, "_text_notes"):
            self._text_notes = FilteredElementCollector(self.doc, self.element.Id).OfClass(TextNote).ToElementIds().Count
        return self._text_notes

    @property
    def obj(self):
        res = {
            "element_id": str(self.element.Id.IntegerValue),
            "element_name": self.element.Title,
            "text_notes_on_sheet": self.text_notes
        }
        for i in self.childs:
            for key, value in i.obj.items():
                if key == "element_id" or key == "element_name":
                    continue 
                res.setdefault(key, 0)
                res[key] += value
        return res
