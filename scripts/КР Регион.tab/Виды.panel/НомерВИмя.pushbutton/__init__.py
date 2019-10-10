import re
from Autodesk.Revit.DB import Transaction, BuiltInCategory, Category, CategorySet, TypeBinding, FilteredElementCollector, Viewport, BuiltInParameter
from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent

doc = __revit__.ActiveUIDocument.Document
views = [doc.GetElement(elId) for elId in __revit__.ActiveUIDocument.Selection.GetElementIds()]
all_views_names = [i.Name for i in FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Views).ToElements()]

keywords = ['азрез', 'рагмент', 'ечение', 'зел', 'азвертка', 'Вид', 'вид']

def recur_add_c(name, names, title, part_name_not_split, c=1):
    test_name = title.replace(part_name_not_split, name)
    if test_name in names:
        add_str = ' (' + to_str(c) + ')'
        test_name = title.replace(part_name_not_split, name + add_str)
        if test_name in names:
            return recur_add_c(name, names,title, part_name_not_split, c=c+1)
        else:
            return test_name
    return test_name

with Transaction(doc, 'Задать номера видов') as t:
    t.Start()
    template = "("
    for keyword in keywords:
        template += '(' + keyword + ')'
        if not keywords.index(keyword) == len(keywords) - 1:
            template += '|'
    template += ')(\s*[а-яА-ЯёЁ0-9-]{1,3}(-[а-яА-ЯёЁ0-9]{1,3})?(\s\(\d+\))?)?'
    template = re.compile(template)
    for view in views:
        title = view.Name
        res = template.search(title)
        if res:
            part_name_not_split = res.group(0)
            part_name = res.group(0).split(' ')
            part_name = part_name[0]
            par = view.GetParameters('Номер вида')[0]
            new_title = part_name + ' ' + par.AsString()
            new_title = recur_add_c(new_title, all_views_names, title, part_name_not_split)
            all_views_names.append(new_title)
            all_views_names.remove(title)
            view.get_Parameter(BuiltInParameter.VIEW_NAME).Set(new_title)
    template = re.compile("\(\d{1,2}\)")
    all_views_names = [i.Name for i in FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Views).ToElements()]
    for view in views:
        title = view.Name
        if template.search(title):
            new_title = template.sub("", title)
            if new_title not in all_views_names:
                view.get_Parameter(BuiltInParameter.VIEW_NAME).Set(new_title)
                all_views_names.remove(title)
    t.Commit()
