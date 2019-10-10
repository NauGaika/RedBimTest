import re
from Autodesk.Revit.DB import Transaction, ParameterElement
from common_scripts.RB_Scheduled import RB_Scheduled
from common_scripts.get_elems.Get_revit_elements import Get_revit_elements

doc = __revit__.ActiveUIDocument.Document
active_view = doc.ActiveView
temp = None
for i in __revit__.Application.Documents:
    if 'Проект' in i.Title:
        temp = i
        break
if temp:
    with Transaction(doc, 'Спецификация арматуры') as t:
        t.Start()
        doc_pb = doc.ParameterBindings
        temp_pb = temp.ParameterBindings
        temp_params = {i.GetDefinition().Name: i for i in Get_revit_elements.get_elems_by_category(temp, ParameterElement)}
        cur_param_to_del = [i.GetDefinition() for i in Get_revit_elements.get_elems_by_category(doc, ParameterElement) if i.GetDefinition().Name not in temp_params.keys()]
        for i in cur_param_to_del:
            if doc_pb.Remove(i):
                echo('Удален параметр ' + i.Name)
        t.Commit()
