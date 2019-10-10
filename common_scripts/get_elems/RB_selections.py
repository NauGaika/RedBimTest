# -*- coding: utf-8 -*-
"""Различные способы выбора элементов из Revit."""

from Autodesk.Revit.DB import Category, BuiltInCategory
from Autodesk.Revit.UI.Selection import ObjectType, ISelectionFilter
from Autodesk.Revit.Exceptions import OperationCanceledException
from common_scripts import echo

doc = __revit__.ActiveUIDocument.Document

class Pick_by_category(ISelectionFilter):
    doc = __revit__.ActiveUIDocument.Document
    def __init__(self, built_in_category):
        if isinstance(built_in_category, Category):
            self.built_in_category = [built_in_category.Id]
        else:
            if isinstance(built_in_category, BuiltInCategory):
                built_in_category = [built_in_category]
            self.built_in_category = [Category.GetCategory(self.doc, i).Id for i in built_in_category]

    def AllowElement(self, el):
        if el.Category.Id in self.built_in_category:
            return True
        return False

    def AllowReference(self, refer, xyz):
        return False

class Pick_by_class(ISelectionFilter):
    doc = __revit__.ActiveUIDocument.Document
    def __init__(self, class_type):
        self.class_type = class_type

    def AllowElement(self, el):
        if isinstance(el, self.class_type):
            return True
        return False

    def AllowReference(self, refer, xyz):
        return False


class RB_selections:
    """Класс с реализацией различных методов выбора элементов."""

    selection = __revit__.ActiveUIDocument.Selection
    doc = __revit__.ActiveUIDocument.Document
    @classmethod
    def pick_element_by_category(cls, built_in_category):
        """Выбор одного элемента по BuiltInCategory."""
        try:
            return cls.doc.GetElement(cls.selection.PickObject(ObjectType.Element, Pick_by_category(built_in_category)))
        except OperationCanceledException:
            return

    @classmethod
    def pick_element_by_class(cls, class_type):
        """Выбор одного элемента по категории."""
        try:
            return cls.doc.GetElement(cls.selection.PickObject(ObjectType.Element, Pick_by_class(class_type)))
        except OperationCanceledException:
            return

    @classmethod
    def pick_elements_by_class(cls, class_type):
        """Выбор одного элемента по категории."""
        try:
            return [cls.doc.GetElement(i) for i in cls.selection.PickObjects(ObjectType.Element, Pick_by_class(class_type))]
        except OperationCanceledException:
            return
