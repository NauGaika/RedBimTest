from Precast import Precast
from Autodesk.Revit.DB import Transaction

doc = __revit__.ActiveUIDocument.Document

with Transaction(doc, "Объединение панелей с элементами узла") as t:
    t.Start()
    obj = Precast(__revit__, analys_geometry=False)
    obj.join_unit_to_panels()
    t.Commit()