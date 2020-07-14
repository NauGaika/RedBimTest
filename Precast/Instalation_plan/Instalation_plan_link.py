# -*- coding: utf-8 -*-
from copy import deepcopy
from common_scripts import echo
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, FamilyInstance, XYZ
from Precast.Panel import Precast_panel
from common_scripts.line_print import Line_printer
from math import pi


class Instalation_plan_link(object):
    rvt_links = {}
    all_panels = {}
    level_parameter = "BDS_LevelNumber"
    section_parameter = "BDS_Section"
    panel_prefix = "215"
    obj_count = 0

    def __init__(self, rvt_link_doc, start_point):
        self.rvt_link_doc = rvt_link_doc
        self.start_point = start_point
        self.sections = {}

    def __repr__(self):
        return "Связь {}".format(self.title)

    @property
    def title(self):
        return self.rvt_link_doc.Title

    def add_level_to_section(self, section, level, transform):
        self.sections.setdefault(section, {})
        level = int(level)
        self.sections[section][level] = transform
        # echo("Добавлен этаж {} в секцию {} для файла {}".format(level, section, self.title))

    @property
    def panels(self):
        if not hasattr(self, "_panels"):
            collector = FilteredElementCollector(self.rvt_link_doc).OfCategory(
                BuiltInCategory.OST_Walls).OfClass(FamilyInstance).ToElements()
            # echo(collector.Count)
            self._panels = [Precast_panel(i, self.rvt_link_doc) for i in collector if i.Symbol.Family.Name[:len(
                self.panel_prefix)] == self.panel_prefix]
            # self._panels = {i.system_tag: i for i in self._panels}
        return self._panels

    def analys_panels(self, to_old=False):
        panels_objs = {}
        for panel in self.panels:
            # echo(panel.system_tag)n
            for section_num, levels in self.sections.items():
                section_num = section_num
                for level, transform in levels.items():
                    level = str(int(level))
                    # Line_printer.print_arc(position - self.start_point)
                    position = self.crutch_of_position(panel)
                    rotation = panel.rotation
                    cur_poition = transform.OfPoint(
                        position) - self.start_point
                    level_str = str(level) if int(level) > 9 else "0" + str(level)
                    colorIndex = panel.get_param("BDS_ColoristicsTag_Floor" + level_str)
                    colorIndex = colorIndex.AsString() if colorIndex else None
                    if to_old:
                        obj = {
                            "mark1": panel.system_tag,
                            "mark2": panel.system_tag,
                            "concrete": "B30",
                            "colorIndex": colorIndex,
                        }
                    else:
                        obj = {
                            "mark": panel.system_tag,
                            "panel": panel,
                            "colorIndex": colorIndex
                        }
                    # Line_printer.print_arc(cur_poition, color="расн")
                    obj["position"] = self.make_xyz(
                        cur_poition, round_count=1, nullable_z=True)
                    # echo(rotation)
                    rot = transform.BasisX.AngleTo(XYZ(1, 0, 0))
                    # echo("__")
                    # echo(rotation)
                    rotation -= rot
                    if round(rotation, 7) < 0:
                        rotation += pi * 2
                    elif round(rotation - 2 * pi, 7) >= 0:
                        rotation -= 2 * pi

                    # echo(rotation)
                    # rotation = round(rotation, 5)
                    # if rotation - 0.00001 == 0:
                    #     rotation = 0.0
                    # echo(rotation)
                    obj["rotation"] = rotation
                    panels_objs.setdefault(section_num, {})
                    panels_objs[section_num].setdefault(level, [])
                    panels_objs[section_num][level].append(obj)
        return panels_objs

    def crutch_of_position(self, panel):
        "Костыль пересчета позиции."
        position = panel.start_point
        position -= panel.vect_abscis * (panel.get_param("BDS_Thickness").AsDouble() / 304.8)# - panel.get_param("Привяза к оси вдоль").AsDouble())
        #position += panel.vect_ordinat * panel.get_param("Привяза к оси_Верхний торец").AsDouble()
        return position

    @classmethod
    def create(cls, rvt_links, start_point):
        for rvt_link in rvt_links:
            rvt_link_doc = rvt_link.GetLinkDocument()
            if rvt_link_doc:
                title = rvt_link_doc.Title
                if title not in cls.rvt_links.keys():
                    cls.rvt_links[title] = cls(rvt_link_doc, start_point)
                level = rvt_link.LookupParameter(cls.level_parameter)
                section = rvt_link.LookupParameter(cls.section_parameter)
                if level and section:
                    level = "%d" % level.AsDouble()
                    section = section.AsString()
                    if not level:
                        echo("У связи {} не задан параметр {}".format(
                            title, cls.level_parameter))
                    elif not section:
                        echo("У связи {} не задан параметр {}".format(
                            title, cls.section_parameter))
                    else:
                        cls.rvt_links[title].add_level_to_section(
                            section, level, rvt_link.GetTransform())
                else:
                    echo("Для связи {} не добавлен параметр {} либо {}".format(
                        title, cls.level_parameter, cls.section_parameter))

    @classmethod
    def find_panels_in_links(cls, to_old=False):
        global_obj = {}
        for i in cls.rvt_links.values():
            res = i.analys_panels(to_old=to_old)
            for section, levels in res.items():
                for level, panels in levels.items():
                    global_obj.setdefault(section, {})
                    global_obj[section].setdefault(level, [])
                    global_obj[section][level] += panels
        return global_obj

    @classmethod
    def all_panel_dict_old(cls, obj, common_data, axis):
        "Преобразовываем в формат для колористики"
        all_panels_old = []
        for sec_num, section in obj.items():
            cur_com_data = deepcopy(common_data)
            cur_com_data["sectionName"] = sec_num
            cur_com_data["fullName"] = sec_num
            cur_com_data["assemblyData"] = {}
            cur_com_data["assemblyData"]["axes"] = axis
            cur_com_data["assemblyData"]["levels"] = []
            for level_num, level in section.items():
                new_obj = {
                    "level": level_num,
                    "precast": level,
                }
                cur_com_data["assemblyData"]["levels"].append(new_obj)
            all_panels_old.append(cur_com_data)
        return all_panels_old

    @staticmethod
    def make_xyz(point, to_mm=True, round_count=5, nullable_z=False, nullable_x=False, nullable_y=False):
        "Преобразовывает ревитовские оси в json."
        return {
            "X": (1 - nullable_x) * round(point.X * (304.8 * to_mm + (1 - to_mm)), round_count),
            "Y": (1 - nullable_y) * round(point.Y * (304.8 * to_mm + (1 - to_mm)), round_count),
            "Z": (1 - nullable_z) * round(point.Z * (304.8 * to_mm + (1 - to_mm)), round_count)
        }
