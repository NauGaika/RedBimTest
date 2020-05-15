# -*- coding: utf-8 -*-
from Autodesk.Revit.DB import *
doc = __revit__.ActiveUIDocument.Document

walls = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType()

with Transaction(doc, "Подсчёт длин") as t:
    t.Start()
    for i in walls:
		i.LookupParameter("BS_Длина").Set(i.LookupParameter("Длина").AsDouble())
    t.Commit()          