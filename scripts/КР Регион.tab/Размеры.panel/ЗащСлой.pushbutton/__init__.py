import re
from Autodesk.Revit.DB import Dimension, Transaction

doc = __revit__.ActiveUIDocument.Document
dims = [doc.GetElement(elId) for elId in __revit__.ActiveUIDocument.Selection.GetElementIds()]
prefix = 'з.с.'
with Transaction(doc, 'Добавить префикс з.с.') as t:
    t.Start()
    for dim in dims:
        if isinstance(dim, Dimension):
                arr = list(dim.Segments)
                if arr:
                    arr[0].Prefix = prefix
                    arr[-1].Prefix = prefix
                else:
                    dim.Prefix = prefix
    t.Commit()
