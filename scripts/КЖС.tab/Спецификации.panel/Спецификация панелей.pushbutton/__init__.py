from Precast import Precast
from Autodesk.Revit.DB import Transaction, RevitLinkInstance, FilteredElementCollector, Wall, FamilyInstance, BuiltInCategory, ViewDuplicateOption
from Autodesk.Revit.DB import ViewSchedule, LinkedFileStatus
from common_scripts.RB_Scheduled import RB_Scheduled
import json
from math import ceil
import re

uidoc = __revit__.ActiveUIDocument
curview = uidoc.ActiveGraphicalView
doc = __revit__.ActiveUIDocument.Document

els = FilteredElementCollector(doc).OfClass(RevitLinkInstance).WhereElementIsNotElementType().ToElements()
els = [i for i in els if doc.GetElement(i.GetTypeId()).GetLinkedFileStatus() == LinkedFileStatus.Loaded]

panel_prefix = "215"
panel_prefix_parametrical = "214"

# 
# 
# Пофиксить ошибку с несколькими секциями. Нужно хранить секции и в них уврони а не на одном уровне
# Сделать обновление спецификации. Как? Заполнить в спецификации параметр главная спецификация. Получить циферку в конце. 
# И обновлять по этой циферке.
# 
# 
all_docs = {}
all_sections_with_levels = {}
for i in els:
    link_doc = i.GetLinkDocument()
    all_docs.setdefault(link_doc, {"levels": set(), "sections": set()})
    level = int(i.LookupParameter("BDS_LevelNumber").AsDouble())
    section = i.LookupParameter("BDS_Section").AsString()
    # echo(level)
    # echo(section)
    all_docs[link_doc].setdefault(section, {})
    all_docs[link_doc][section].setdefault(level, set())
    if section:
        all_sections_with_levels.setdefault(section, set())
        all_sections_with_levels[section].add(level)
    else:
        echo("Для {} не задан параметр BDS_Section".format(link_doc.Title))

# all_levels = list(all_levels)
# all_sections = list(all_sections)
all_sections = list(all_sections_with_levels.keys())
for i in all_sections_with_levels.keys():
    all_sections_with_levels[i] = list(all_sections_with_levels[i])
    all_sections_with_levels[i].sort()
# all_levels.sort()

all_sections.sort(reverse=True)
# echo(all_sections_with_levels)
tags = {}
# echo(all_sections)
for link_doc, sections in all_docs.items():
    sections_num = sections.keys()
    panels = FilteredElementCollector(link_doc).OfCategory(BuiltInCategory.OST_Walls).OfClass(FamilyInstance)
    # panels.UnionWith(FilteredElementCollector(link_doc).OfCategory(BuiltInCategory.OST_Columns).OfClass(FamilyInstance))
    panels = panels.ToElements()
    panels = [i for i in panels if i.Symbol.Family.Name[:len(panel_prefix)] == panel_prefix or i.Symbol.Family.Name[:len(panel_prefix_parametrical)] == panel_prefix_parametrical]
    for panel in panels:
        # echo(link_doc.Title)
        symb = panel.Symbol
        tag = ""
        pref_tag = symb.LookupParameter("BDS_MarkPrefix")
        if pref_tag:
            tag += pref_tag.AsString()
        fas_tag = panel.Symbol.LookupParameter("BDS_FacadeType")
        if fas_tag:
            tag += fas_tag.AsString()
        sub_tag = panel.Symbol.LookupParameter("BDS_MarkSubPrefix")
        if sub_tag and sub_tag.AsString():
            tag += "-" + sub_tag.AsString()
        tag_par = panel.LookupParameter("BDS_Tag")
        tag_par = tag_par if tag_par else panel.Symbol.LookupParameter("BDS_Tag")
        tag += "-" + tag_par.AsString()
        if tag:
            for section in sections_num:
                for level in sections[section]:
                    level_str = str(level) if level > 9 else "0" + str(level)
                    # echo("BDS_СoloristicsTag_Floor" + level_str)
                    coloristic_mark = panel.LookupParameter("BDS_СoloristicsTag_Floor" + level_str).AsString()
                    new_tag = tag
                    if coloristic_mark:
                        new_tag = "{} ({})".format(new_tag, coloristic_mark)
                    tags.setdefault(new_tag, {
                            "album": None,
                            "mass": panel.LookupParameter("BDS_Mass").AsDouble(),
                            "sections": {},
                            "length": panel.LookupParameter("BDS_Length").AsDouble(),
                            "height": panel.LookupParameter("BDS_Height").AsDouble(),
                            "thick": panel.LookupParameter("BDS_Thickness").AsDouble(),
                            "hole": panel.LookupParameter("BDS_Hole").AsString(),
                            "volume": panel.LookupParameter("BDS_Volume").AsDouble()
                        })
                    tags[new_tag]["sections"].setdefault(section, {})
                    tags[new_tag]["sections"][section].setdefault(level, 0)
                    tags[new_tag]["sections"][section][level] += 1


# echo(tags)
res = []
for tag, obj in tags.items():
    obj["tag"] = tag
    res.append(obj)


tags = res
tags.sort(key=lambda x: x["tag"])

def create_head(view, tags, name, prefix_name=""):
    sched = RB_Scheduled(view)
    sched.remove_all_row_and_column()
    
    width = [50, 75, 20]
    section_width = []
    for i in all_sections_with_levels.values():
        section_width += [7.5 for i in range(len(i))]
        section_width.append(12)
    width += section_width
    width += [12.5, 15.5, 18.5, 22, 76, 26.5]
    summ_width = sum(width)
    sched.set_table_width(summ_width)
    sched.set_column_count(len(width))
    sched.set_columns_width(width)
    sched.add_rows(0, len(tags) + 4)

    sched.merge_cell(0, 0, len(width) - 1, 0)
    if prefix_name:
        sched_name = "{} ({})".format(name, prefix_name)
    else:
        sched_name = name
    sched.set_row_val(0, 0, sched_name)

    sched.set_cell_border(0, 0, False, False, False, True)
    sched.set_cell_font_size(0, 0, 3.5)

    merged_column = []
    merged_column.append((0, 1, 0, 3))
    sched.set_row_val(0, 1, "Альбом рабочих чертжей")
    merged_column.append((1, 1, 1, 3))
    sched.set_row_val(1, 1, "Марка")
    merged_column.append((2, 1, 2, 3))
    sched.set_row_val(2, 1, "Масса")
    for i in merged_column:
        sched.merge_cell(*i)
    # level_count = 0
    # for i in all_sections:
    #     level_count += len(all_sections[i])
    # pp = None
    start = len(merged_column)
    all_sections_keys = list(all_sections_with_levels.keys())
    all_sections_keys.sort()
    for section in all_sections_keys:
        levels = all_sections_with_levels[section]
        sched.set_row_val(start, 2, "Секция " + section)
        end = start
        for level in levels:
            sched.set_row_val(end, 3, str(level) + "эт")
            end += 1
        sched.merge_cell(start, 2, end, 2)
        sched.set_row_val(end, 3, "Всего")
        end +=  1
        start = end
    end -= 1
    sched.merge_cell(len(merged_column), 1, end, 1)
    sched.set_row_val(len(merged_column), 1, "Количество изделий, шт")

    end += 1
    sched.set_row_val(end, 1, "Всего")
    sched.merge_cell(end, 1, end, 3)

    end += 1
    sched.set_row_val(end, 1, "Длина, мм")
    sched.merge_cell(end, 1, end, 3)

    end += 1
    sched.set_row_val(end, 1, "Высота, мм")
    sched.merge_cell(end, 1, end, 3)

    end += 1
    sched.set_row_val(end, 1, "Толщина, мм")
    sched.merge_cell(end, 1, end, 3)

    end += 1
    sched.set_row_val(end, 1, "Проем")
    sched.merge_cell(end, 1, end, 3)

    end += 1
    sched.set_row_val(end, 1, "Объем изделия, м³")
    sched.merge_cell(end, 1, end, 3)

    start = 4
    
    for obj in tags:
        hor = 1
        sched.set_row_val(hor, start, obj["tag"])
        hor += 1
        sched.set_row_val(hor, start, obj["mass"], rounded=0)

        panel_summ = 0
        for section in all_sections_keys:
            panel_section_summ = 0
            levels = all_sections_with_levels[section]
            for level in levels:
                hor += 1
                val = 0
                if section in obj["sections"].keys() and level in obj["sections"][section].keys():
                    val = obj["sections"][section][level]
                    panel_section_summ += val
                if val == 0:
                    sched.set_row_val(hor, start, "-")
                else:
                    sched.set_row_val(hor, start, val)
            hor += 1
            sched.set_row_val(hor, start, panel_section_summ)
            panel_summ += panel_section_summ
        hor += 1
        sched.set_row_val(hor, start, panel_summ)

        hor += 1
        sched.set_row_val(hor, start, obj["length"], rounded=0)
        hor += 1
        sched.set_row_val(hor, start, obj["height"], rounded=0)
        hor += 1
        sched.set_row_val(hor, start, obj["thick"], rounded=0)
        hor += 1
        sched.set_row_val(hor, start, obj["hole"])
        hor += 1
        sched.set_row_val(hor, start, obj["volume"], rounded=2)
        start += 1
    # echo(start)
    sched.set_cell_border(start-1, 0, True, True, True, True)

max_rows = 47
with Transaction(doc, "Сформировать таблицу коллористики") as t:
    t.Start()
    count_of_sheet = int(ceil(float(len(tags)) / max_rows))
    if count_of_sheet > 0:
        name = curview.Name
        templ_replace = re.compile("((\s)*(\(Окончание\))|(\(Начало\))|(\(Продолжение\)))((\s*\d+\s*)$)".format(name))
        name = templ_replace.sub("", name)
        templ_find = re.compile("(^({})\s*)((\(Окончание\))|(\(Начало\))|(\(Продолжение\)))((\s+\d+)$)".format(name))
        repl_sheds = FilteredElementCollector(doc).OfClass(ViewSchedule).ToElements()
        repl_sheds = [i for i in repl_sheds if templ_find.search(i.Name)]
        privious_sched = []
        number_in_end = re.compile("\d+$")
        repl_sheds.sort(key=lambda x: int(number_in_end.search(x.Name).group(0)))
        if len(repl_sheds) > count_of_sheet:
            echo(repl_sheds[-1].Name, " лишняя спецификация при количестве элементов ", len(tags))
        if not repl_sheds:
            repl_sheds = [doc.ActiveView]
        for i in range(0, count_of_sheet):
            if i == 0:
                prefix_name = "Начало"
            elif i != count_of_sheet - 1:
                prefix_name = "Продолжение"
            else:
                prefix_name = "Окончание"
            if i > len(repl_sheds)-1:
                cre_view = doc.GetElement(curview.Duplicate(ViewDuplicateOption.Duplicate))
            else:
                cre_view = repl_sheds[i]
            if count_of_sheet == 1:
                prefix_name = ""
            else:
                cre_view.Name = "{} ({}) {}".format(name, prefix_name, i)
            tags_slice = tags[i * max_rows: (i + 1) * max_rows]
            create_head(cre_view, tags_slice, name, prefix_name=prefix_name)
    else:
        echo("Не найдено элементов панели")

    t.Commit()



#     #     start += 1
#     t.Commit()
# for tag, levels in tags.items()
#     level_count = 


    # for level in levels:

    # echo(i.LookupParameter("BDS_LayerNumber").AsInteger())
    # panels = FilteredElementCollector(i.Document).OfCategory(BuiltInCategory.OST_Walls).ToElements()
    # for j in panels:
    #     echo(j)

# with Transaction(doc, "Объединение заполнение массы") as t:
#     t.Start()
#     obj = Precast(doc)
#     obj.set_mass()
#     t.Commit()