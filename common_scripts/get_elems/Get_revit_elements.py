# -*- coding: utf-8 -*-
"""Различные способы получения элементов из документа Revit."""

from Autodesk.Revit.DB import FilteredElementCollector, ElementClassFilter
from common_scripts import *
doc = __revit__.ActiveUIDocument.Document


class Get_revit_elements:
    """Класс для поиска элементов в Revit."""

    @classmethod
    def get_elems_by_category(cls, doc, category_class, active_view=None, name=None):
        """Получение элемента по классу категории."""
        if not active_view:
            els = FilteredElementCollector(doc).OfClass(category_class).\
                  ToElements()
        else:
            els = FilteredElementCollector(doc, active_view).\
                  OfClass(category_class).ToElements()
        if name:
            els = [i for i in els if name in i.Name] 
        return els

    @classmethod
    def get_elems_by_builtinCategory(cls, built_in_cat, include=[],
                                     active_view=None):
        """Получение элемента по встроенному классу."""
        if not include:
            if not active_view:
                els = FilteredElementCollector(doc).OfCategory(built_in_cat)
            else:
                els = FilteredElementCollector(doc, active_view).\
                      OfCategory(built_in_cat)
            return els.ToElements()
        if include:
            new_list = []
            for i in include:
                if not active_view:
                    els = FilteredElementCollector(doc).OfCategory(built_in_cat)
                else:
                    els = FilteredElementCollector(doc, active_view).\
                          OfCategory(built_in_cat)
                new_list += els.OfClass(i).ToElements()
            return new_list
