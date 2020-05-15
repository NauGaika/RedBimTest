import sys
from datetime import datetime
from common_scripts.Template import Template

from System.Collections.Generic import List

from Autodesk.Revit.DB import Transaction, ViewSheet, BuiltInParameter, ElementId, FilteredElementCollector, ParameterFilterElement
from Autodesk.Revit.DB import ElementTransformUtils, Transform, CopyPasteOptions

active_doc = __revit__.ActiveUIDocument.Document
template_file_path = '\\\\picompany.ru\\pikp\\Dep\\LKP4\\WORK\\Шаблоны видов\\Шаблоны видов.rvt'
comparison_paths = '\\\\picompany.ru\\pikp\\Dep\\LKP4\\WORK\\Шаблоны видов\\Сопоставления'

active_view = None
if isinstance(active_view, ViewSheet):
    if __revit__.ActiveUIDocument.Selection.GetElementIds():
        view_sheet = [active_doc.GetElement(elId) for elId in __revit__.ActiveUIDocument.Selection.GetElementIds()][0]
        active_view = active_doc.GetElement(view_sheet.ViewId)
else:
    active_view = active_doc.ActiveView

cur_template_id = active_view.ViewTemplateId
if cur_template_id == ElementId.InvalidElementId:
    sys.exit(0)
file_with_template = Template(template_file_path)
doc_kit = file_with_template.define_kit(active_doc)
source_doc = file_with_template.open_source()

# for i in __revit__.Application.Documents:
#     if i.Title == "Шаблоны видов":
#         source_doc = i



echo("***", "Имя текущего шаблона " + active_doc.GetElement(cur_template_id).Title)
echo("***", "Находим виды к которым применен шаблон")
view_with_templates = file_with_template.get_all_view_with_template(active_doc, cur_template_id)
cur_template = active_doc.GetElement(cur_template_id)
template_name = cur_template.get_Parameter(BuiltInParameter.VIEW_NAME)
source_templates = file_with_template.find_all_view_template(source_doc)
echo("***", "Получили все шаблоны из файла с шаблонами")
all_exist_templates = file_with_template.all_file_comparisions(comparison_paths, doc_kit)

# echo("***", "Определяем комплект чертежей")
# file_with_template.define_kit(active_doc)
source_template_id = None
for i in all_exist_templates.keys():
    if template_name.AsString() in i:
        source_template_id = ElementId(all_exist_templates[i])
        break

if source_template_id:
    with Transaction(active_doc, 'Обновить шаблон') as t:
        t.Start()
        source_template = source_doc.GetElement(source_template_id)
        echo("Найден соответствующий шаблон " + source_template.Title)
        cur_time = '_old_' + datetime.now().strftime("%y%m%d%H%M%S")

        source_template_filter_names = { source_doc.GetElement(i).Name: i for i in source_doc.GetElement(source_template_id).GetFilters()}
        for i in FilteredElementCollector(active_doc).OfClass(ParameterFilterElement).ToElements():
            if i.Name in source_template_filter_names.keys():
                i.Name += cur_time
        template_name.Set(template_name.AsString() + cur_time)

        new_template = List[ElementId]([source_template_id])
        new_template = ElementTransformUtils.CopyElements(source_doc, new_template, active_doc, Transform.Identity, CopyPasteOptions())
        for i in new_template:
            new_template_name = active_doc.GetElement(i).get_Parameter(BuiltInParameter.VIEW_NAME)
            new_template_name_str = file_with_template.rename_template(new_template_name.AsString())
            new_template_name.Set(new_template_name_str)
            echo("Скопирован шаблон " + new_template_name_str)
            for k in view_with_templates:
                k.ViewTemplateId = i
            break
        t.Commit()
else:
    echo("Соответствующий шаблон не найден. Необходимо задать сопоставления в " + comparison_paths)
# with Transaction(active_doc, 'Обновить шаблон') as t:
#     t.Start()
#     if active_view:
#
#         #
#         # cur_time = '_old_' + datetime.now().strftime("%y%m%d%H%M%S")
#         # new_name = template_name.AsString() + cur_time
#         # template_name.Set(new_name)
#         # echo("***", "Изменили имя шаблона вида на " + new_name)
#     t.Commit()


# current_templates = file_with_template.find_all_view_template(active_doc)
