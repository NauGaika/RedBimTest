from Precast.Instalation_plan import Instalation_plan
from Autodesk.Revit.DB import Transaction

doc = __revit__.ActiveUIDocument.Document
ip = Instalation_plan(doc)
ip.check_all_panels()