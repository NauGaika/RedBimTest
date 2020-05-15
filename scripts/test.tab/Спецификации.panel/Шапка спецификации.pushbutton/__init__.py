import re
from Autodesk.Revit.DB import Transaction, GraphicsStyle
from common_scripts.RB_Scheduled import RB_Scheduled
from common_scripts.get_elems.Get_revit_elements import Get_revit_elements

doc = __revit__.ActiveUIDocument.Document
active_view = doc.ActiveView
with Transaction(doc, 'Спецификация арматуры') as t:
    t.Start()
    sched = RB_Scheduled(doc)
    sched.remove_all_row_and_column()
    sched.set_column_count(6)
    sched.set_row_width(arr=[15, 60, 65, 12, 13, 20])
    sched.add_rows(0, count=4)
    sched.merge_cell(0, 0, 0, 5)
    sched.set_row_list(1, ['Поз.', "Обозначение", "Наименование", "Кол.", "Масса", "Примечание"])

    sched.merge_cell(2, 0, 2, 5)
    title = doc.ActiveView.Name
    temp = re.compile("\*.+\*")
    res = temp.search(title)
    if res:
        res = res.group(0)
        res = res.replace("*", '')
        if res:
            title = res
    sched.set_row_val(0, 0, title)
    sched.set_row_val(0, 2, "Конструкция")
    sched.merge_cell(3, 0, 3, 5)
    sched.set_row_val(0, 3, "Детали")
    sched.set_row_height(8, row_num=-1)
    t.Commit()
