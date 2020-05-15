import re
from math import pi
from Autodesk.Revit.DB import BuiltInCategory, BuiltInParameter, Transaction, FilteredElementCollector, ParameterFilterElement, ViewSheet, ScheduleSheetInstance, ElementId, ViewDuplicateOption, ScheduleFilter, ScheduleSheetInstance


doc = __revit__.ActiveUIDocument.Document
t = Transaction(doc, 'Тестирование')
t.Start()

view_sheets = [doc.GetElement(elId) for elId
             in __revit__.ActiveUIDocument.Selection.GetElementIds()]
sheduled_dict = {}
templateId = ElementId(4577689)
templade = doc.GetElement(templateId)
old_field_name = {}
sheduled_instances = FilteredElementCollector(doc).OfClass(ScheduleSheetInstance).ToElements()
for sheduled_instance in sheduled_instances:
    scheduled = doc.GetElement(sheduled_instance.ScheduleId)
    view_sheet = doc.GetElement(sheduled_instance.OwnerViewId)
    if 'Спецификация арматуры' in scheduled.Title and scheduled.Id != templateId:
        if int(str(scheduled.Id)) not in sheduled_dict.keys():
            sheduled_dict.update({int(str(scheduled.Id)): [(view_sheet, sheduled_instance.Point)]})
        else:
            sheduled_dict[int(str(scheduled.Id))].append((view_sheet, sheduled_instance.Point))
for s_id, value in sheduled_dict.items():
    shed = doc.GetElement(ElementId(s_id))
    title = shed.get_Parameter(BuiltInParameter.VIEW_NAME).AsString()
    filters = shed.Definition.GetFilters()
    new_shed = doc.GetElement(templade.Duplicate(ViewDuplicateOption.Duplicate))
    all_fields = {new_shed.Definition.GetField(num).GetName(): new_shed.Definition.GetFieldId(num) for num in range(0, new_shed.Definition.GetFieldCount())}
    for filter in filters:
        field_name = shed.Definition.GetField(filter.FieldId).GetName()
        filt_type = filter.FilterType
        if filter.IsStringValue:
            filt_value = filter.GetStringValue()
        elif filter.IsIntegerValue:
            filt_value = filter.GetIntegerValue()
        elif filter.IsDoubleValue:
            filt_value = filter.GetDoubleValue()
        elif filter.IsElementIdValue:
            filt_value = filter.GetElementIdValue()
        else:
            continue
        if field_name in old_field_name.keys():
            field_id = all_fields[old_field_name[field_name]]
        elif field_name in all_fields.keys():
            field_id = all_fields[field_name]
        else:
            continue
        new_filter = ScheduleFilter(field_id, filt_type, filt_value)
        new_shed.Definition.AddFilter(new_filter)
    for sheet, point in value:
        ScheduleSheetInstance.Create(doc, sheet.Id, new_shed.Id, point)
    doc.Delete(shed.Id)
    echo(title)
    new_shed.get_Parameter(BuiltInParameter.VIEW_NAME).Set(title + ' ok')
t.Commit()