# coding: utf8
"""Добавляем необходимые фильтры для КЖ"""

from Autodesk.Revit.DB import Transaction, ElementId

from Autodesk.Revit.DB.Structure import RebarInSystem
from System.Collections.Generic import List



uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
curview = uidoc.ActiveGraphicalView
selection = [doc.GetElement(elId) for elId in __revit__.ActiveUIDocument.Selection.GetElementIds()]

t=Transaction(doc, 'tt')
t.Start()
if selection:
    if isinstance(selection[0], RebarInSystem):
        __revit__.ActiveUIDocument.Selection.SetElementIds(List[ElementId]([selection[0].SystemId]))
t.Commit()