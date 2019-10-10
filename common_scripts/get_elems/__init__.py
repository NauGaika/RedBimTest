# -*- coding: utf-8 -*-
import clr
from Autodesk.Revit.DB import BuiltInCategory, Category
from Autodesk.Revit.UI.Selection import ObjectType,ISelectionFilter
from common_scripts import *
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

class Pick_by_category(ISelectionFilter):
    def __init__(self, cat):
        if isinstance(cat, BuiltInCategory):
            self.cat_name = Category.GetCategory(doc, cat).Name
        else:
            self.cat_name = cat.Name
    def AllowElement(self, el):
        if self.cat_name == el.Category.Name:
            return True
        else:
            return False
    def AllowReference(self, refer, xyz):
        return False

def get_elem_by_click(built_in_cat):
    filter = Pick_by_category(built_in_cat)
    ref = uidoc.Selection.PickObject(ObjectType.Element, filter)
    el = doc.GetElement(ref)
    return el
