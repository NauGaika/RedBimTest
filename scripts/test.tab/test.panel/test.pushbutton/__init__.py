from Precast.PrecastCreator.PrecastPanelCreator import PrecastPanelCreator
from Autodesk.Revit.DB import Transaction
import datetime

doc = __revit__.ActiveUIDocument.Document
start_time = datetime.datetime.now()
with Transaction(doc, "Проверка панелей на наличие в базе") as t:
    t.Start()
    obj = PrecastPanelCreator(__revit__)
    obj.create_test_panel()
    t.Commit()
echo("Затрачено {} времени".format(datetime.datetime.now() - start_time))