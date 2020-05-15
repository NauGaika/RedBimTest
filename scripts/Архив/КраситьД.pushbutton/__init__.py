import re
from Autodesk.Revit.DB import Transaction, ParameterElement, XYZ, ParameterFilterElement
from Autodesk.Revit.DB import ParameterFilterRuleFactory, ElementId, FilterRule
from Autodesk.Revit.DB import BuiltInCategory, OverrideGraphicSettings
from Autodesk.Revit.UI import ColorSelectionDialog, ItemSelectionDialogResult
from common_scripts.RB_Scheduled import RB_Scheduled
from common_scripts.get_elems.Get_revit_elements import Get_revit_elements

from System.Collections.Generic import List

doc = __revit__.ActiveUIDocument.Document
el = [doc.GetElement(elId) for elId in __revit__.ActiveUIDocument.Selection.GetElementIds()]
def create_filter(diam, par):
    filt_name = 'Арм.d' + to_str(int(diam))
    all_filters = Get_revit_elements.get_elems_by_category(doc, ParameterFilterElement)
    all_filters = {i.Name: i for i in all_filters}
    if filt_name not in all_filters.keys():
        categories = List[ElementId]()
        categories.Add(ElementId(BuiltInCategory.OST_Rebar))
        filter_rules = List[FilterRule]()
        filter_rule = ParameterFilterRuleFactory.CreateEqualsRule(par.Id, to_feet(diam), to_feet(0.1))
        filter_rules.Add(filter_rule)
        filter = ParameterFilterElement.Create(doc, filt_name, categories)
        filter.SetRules(filter_rules)
    else:
        filter = all_filters[filt_name]
    return filter

t = Transaction(doc, 'Разукрасить')
t.Start()
if el:
    el = el[0]
    par = el.GetParameters("Рзм.Диаметр")
    if el.GetParameters("Рзм.Диаметр"):
        par = el.GetParameters("Рзм.Диаметр")[0]
    elif doc.GetElement(el.GetTypeId()).GetParameters("Рзм.Диаметр"):
        par = doc.GetElement(el.GetTypeId()).GetParameters("Рзм.Диаметр")[0]
    if par:
        diam = to_mm(par.AsDouble())
        sel_color = ColorSelectionDialog()
        if sel_color.Show() == ItemSelectionDialogResult.Confirmed:
            color = sel_color.SelectedColor
            filter = create_filter(diam, par)
            active_view = doc.ActiveView
            if active_view.IsFilterApplied(filter.Id):
                active_view.RemoveFilter(filter.Id)
            over = OverrideGraphicSettings()
            over.SetProjectionLineColor(color)
            over.SetCutLineColor(color)
            active_view.AddFilter(filter.Id)
            active_view.SetFilterOverrides(filter.Id, over)
            if active_view.ViewTemplateId != ElementId.InvalidElementId and active_view.ViewTemplateId:
                template = active_view.ViewTemplateId
                if template.IsFilterApplied(filter.Id):
                    template.RemoveFilter(filter.Id)
                doc.GetElement(active_view.ViewTemplateId).AddFilter(filter.Id)
                doc.GetElement(active_view.ViewTemplateId).SetFilterOverrides(filter.Id, over)

t.Commit()
