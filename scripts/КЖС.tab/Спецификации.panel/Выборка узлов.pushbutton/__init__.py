from Precast import Precast
from Autodesk.Revit.DB import Transaction, RevitLinkInstance, \
FilteredElementCollector, FamilyInstance, BuiltInCategory, ViewDuplicateOption
from Autodesk.Revit.DB import ViewSchedule, LinkedFileStatus
from common_scripts.RB_Scheduled import RB_Scheduled
import json
from math import ceil
import re


def get_parameter(element, parameter):
    par = element.LookupParameter(parameter)
    return par if par else element.Symbol.LookupParameter(parameter)

uidoc = __revit__.ActiveUIDocument
curview = uidoc.ActiveGraphicalView
doc = __revit__.ActiveUIDocument.Document

els = FilteredElementCollector(doc).OfClass(RevitLinkInstance).WhereElementIsNotElementType().ToElements()
els = [i for i in els if doc.GetElement(i.GetTypeId()).GetLinkedFileStatus() == LinkedFileStatus.Loaded]

panel_prefix = "215"

all_docs = {}
all_sections_with_levels = {}
for i in els:
    link_doc = i.GetLinkDocument()
    level = int(i.LookupParameter("BDS_LevelNumber").AsDouble())
    section = i.LookupParameter("BDS_Section").AsString()
    all_docs.setdefault(link_doc, {})
    all_docs[link_doc].setdefault(section, {})
    all_docs[link_doc][section].setdefault(level, set())
    all_sections_with_levels.setdefault(section, set())
    all_sections_with_levels[section].add(level)

all_sections = list(all_sections_with_levels.keys())
for i in all_sections_with_levels.keys():
    all_sections_with_levels[i] = list(all_sections_with_levels[i])
    all_sections_with_levels[i].sort()

# echo(all_docs)
tags = {}
for link_doc, sections in all_docs.items():
    sections_num = sections.keys()
    generic_models = FilteredElementCollector(link_doc).OfCategory(
        BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType()

    for generic_model in generic_models:
        par = get_parameter(generic_model, "BDS_ElementType")
        if par:
            val = par.AsDouble()
            if val == 7:
                par = get_parameter(generic_model, "Precast_GeneralJoint")
                par = par if par else get_parameter(generic_model, "Precast_GeneralJoin")
                if par and par.AsInteger():
                    mark_name = get_parameter(generic_model, "BDS_Tag")
                    mark_name = mark_name.AsString() if mark_name else "Н/О"
                    tags.setdefault(mark_name, {})
                    for section_num, section in sections.items():
                        tags[mark_name].setdefault(section_num, {})
                        for level_num, level in section.items():
                            tags[mark_name][section_num].setdefault(level_num, 0)
                            tags[mark_name][section_num][level_num] += 1

curview = uidoc.ActiveGraphicalView

def create_head(view, tags, name):
    if tags:
        sched = RB_Scheduled(view)
        sched.remove_all_row_and_column()
        sched.set_cell_border(0, 0, True, True, True, True)
        width = [9, 12]
        section_width = []
        for i in all_sections_with_levels.values():
            section_width += [7.5] * len(i)
            section_width.append(10)
        width += section_width
        width += [17.5]
        summ_width = sum(width)
        sched.set_table_width(summ_width)
        sched.set_column_count(len(width))
        sched.set_columns_width(width)
        sched.add_rows(0, len(tags) + 4)

        sched.merge_cell(0, 4, 0, len(tags) + 3)

        sched.merge_cell(0, 0, len(width) - 1, 0)
        sched.set_row_val(0, 0, name)
        sched.set_cell_border(0, 0, False, False, False, True)
        sched.set_cell_font_size(0, 0, 3.5)

        sched.set_row_val(0, 1, "№ Узлов")
        sched.merge_cell(0, 1, 1, 3)

        start = 2
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

        sched.merge_cell(2, 1, end, 1)
        sched.set_row_val(2, 1, "Количество на секцию, шт")

        end += 1
        sched.set_row_val(end, 1, "Всего")
        sched.merge_cell(end, 1, end, 3)

        start = 3
        # echo(json.dumps(tags))
        for tag, sections in tags.items():
            hor = 1
            start += 1
            sched.set_row_val(hor, start, tag)
            hor+= 1
            gen_sum = 0
            for section in all_sections_keys:
                levels = all_sections_with_levels[section]
                sum_ = 0
                for level in levels:
                    if section in sections.keys() and level in sections[section].keys():
                        val = sections[section][level]
                        sum_ += val
                    else:
                        val = "-"
                    sched.set_row_val(hor, start, val)
                    hor += 1
                sched.set_row_val(hor, start, sum_)
                gen_sum += sum_
            hor += 1
            sched.set_row_val(hor, start, gen_sum)
    else:
        return "Не загружены связи, либо закрыты рабочие наборы со связями, либо подходящих элементов нет"



with Transaction(doc, "Выборка монтажных узлов") as t:
    t.Start()
    res = create_head(curview, tags, "Выборка монтажных узлов")
    if res:
        message(res)
    t.Commit()