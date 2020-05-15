from Precast.Instalation_plan import Instalation_plan
from Autodesk.Revit.DB import Transaction

doc = __revit__.ActiveUIDocument.Document
with Transaction(doc, "Сформировать монтажный план.") as t:
    t.Start()
    ip = Instalation_plan(doc)
    ip.create_grid_plan()
    t.Commit()