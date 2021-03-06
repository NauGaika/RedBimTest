# -*- coding: utf-8 -*-
import json
import io
import sys
import httplib
from os import path
from clr import StrongBox
from math import pi
from Autodesk.Revit.DB import FilteredElementCollector, Outline, FamilyInstance, BuiltInCategory
from Autodesk.Revit.DB import Line, XYZ, CurveLoop, SolidCurveIntersectionOptions, SetComparisonResult, IntersectionResultArray
from Autodesk.Revit.DB import BooleanOperationsUtils, BooleanOperationsType, BuiltInParameter
from Autodesk.Revit.DB import AssemblyInstance, ElementId, AssemblyViewUtils

sys.path.append(path.split(path.split(__file__)[0])[0])
from common_scripts import echo, RB_Parameter_mixin
from Common import Precast_component
from Common.Precast_geometry import Precast_geometry
from Common.Precast_validator import Precast_validator
from .Precast_panel_finder import Precast_panel_finder
from .Precast_panel_analys_geometry import Precast_panel_analys_geometry
from .Precast_panel_json import Precast_panel_json
from .Precast_panel_validate import Precast_panel_validate
from .Precast_panel_indastry import Precast_panel_indastry
from System.Collections.Generic import List


class Precast_panel(Precast_component,
                    Precast_panel_validate,
                    Precast_panel_finder,
                    Precast_panel_analys_geometry,
                    Precast_panel_json,
                    Precast_panel_indastry):
    "Сборные панели."

    window_categorys = []
    COLORISTIC_URI = r"vpp-sql04"

    # Префиксы которые используются
    windows_prefix = "221"
    unit_prefix = "219"
    holes_prefix = "232"
    # Марка типа элемента
    # 1 - внешняя панель
    # 2 - внутренняя
    # 3 - перекрытие
    # 4 - объемные элементы
    element_type_parameter_name = "BDS_ElementType"
    mass_parameter_name = "BDS_Mass"
    volume_parameter_name = "BDS_Volume"
    series_parameter_name = "BDS_Series"
    facade_type_parameter_name = "BDS_FacadeType"
    mark_prefix_parameter_name = "BDS_MarkPrefix"
    mark_sub_prefix_parameter_name = "BDS_MarkSubPrefix"
    construction_type_parameter_name = "BDS_ConstructionType"
    advance_mark_parameter_name = "BDS_AdvanceTag"
    system_mark_parameter_name = "BDS_SystemTag"
    mark_parameter_name = "BDS_Tag"
    embedded_part_parameter_value = 5
    unit_parameter_value = 7
    platic_parameter_value = 12

    def __init__(self,
            panel,
            doc=None,
            analys_geometry=False,
            old_format=None,
            develop=False,
            geometrical=False):
        super(Precast_panel, self).__init__(panel, doc, analys_geometry=analys_geometry)
        self.develop = develop
        self.obj = {}
        self.is_analysed = False
        self.geometrical = geometrical
        # Необходимо, чтобы ID определился при создании панели. Для монтажек
        self.Id
        all_panel_parameters = [
            self.mass_parameter_name,
            self.volume_parameter_name,
            self.series_parameter_name,
            self.facade_type_parameter_name,
            self.mark_prefix_parameter_name,
            self.mark_sub_prefix_parameter_name,
            self.construction_type_parameter_name,
            self.advance_mark_parameter_name,
            self.mark_parameter_name,
            self.system_mark_parameter_name,
            "JSON"
        ]
        try:
            # echo(geometrical)
            if self.parameter_is_exists(all_panel_parameters):
                self.series_param = self[self.series_parameter_name]
                self.mark_prefix_param = self[self.mark_prefix_parameter_name]
                # Костыль, который меняет тройку на букву З
                if self.mark_prefix_param:
                    self.mark_prefix_param = self.mark_prefix_param.replace(
                        "ЗНС", "3НС")
                self.facade_type_param = self[self.facade_type_parameter_name] if self[self.facade_type_parameter_name] else ""
                self.mark_sub_prefix_param = self[self.mark_sub_prefix_parameter_name] if self[self.mark_sub_prefix_parameter_name] else ""
                self.construction_type_param = self[self.construction_type_parameter_name] if self[self.mark_sub_prefix_parameter_name] else ""
                if not self.facade_type_param and geometrical:
                    echo("Не указан FacadeType")
                if not self.mark_sub_prefix_param and geometrical:
                    echo("Не указан SubPrefix")
                if not self.construction_type_param and geometrical:
                    echo("Не указан ConstructionType")
                if self.analys_geometry and self.geometrical:
                    self.disassemble()
                    self.make_analys_geometry()
                    self.set_windows_to_panel()
                    self.add_ifc_parameter()
                    self.add_indastry_parameter()
                    # self.assambly = self.make_assambly()
            else:
                echo(
                    "Ошибки в получении параметров у панели {} {}".format(self, sys.exc_info()[1]))
        except:
            echo("Ошибка в панели {} {}".format(self, sys.exc_info()[1]))

    def __repr__(self):
        return "Панель id {}".format(self.element.Id.IntegerValue)

    def parameter_is_exists(self, parameters):
        "Проверяет наличие параметров у элемета."
        all_ok = True
        for i in parameters:
            if not self.get_param(i):
                all_ok = False
                echo("Не найден параметр {}".format(i))
        return all_ok

    @property
    def start_point(self):
        "Точка вставки."
        if not hasattr(self, "_start_point"):
            if self.is_analysed:
                self._start_point = self.ultimate_minimum
            else:
                self._start_point = self.element.Location.Point
        return self._start_point

    @property
    def mass(self):
        all_mass = 0
        for i in self.real_solids:
            all_mass += i.mass
        for i in self.windows:
            for j in i.real_solids:
                all_mass += j.mass
        return round(all_mass, 2)

    def set_mass_parameter(self):
        par = self.element.LookupParameter(self.mass_parameter_name)
        if par:
            par.Set(self.mass)
        else:
            echo("Нет параметра " + self.mass_parameter_name)

    @property
    def volume(self):
        all_volume = 0
        for i in self.solids:
            all_volume += i.volume
        for i in self.windows:
            for j in i.solids:
                all_volume += j.volume
        return round(all_volume, 2)

    def set_volume_parameter(self):
        par = self.element.LookupParameter(self.volume_parameter_name)
        if par:
            par.Set(self.volume)
        else:
            raise Exception("Нет параметра " + self.volume_parameter_name)

    @property
    def advance_tag(self):
        par = self[self.advance_mark_parameter_name]
        return par if par else ""

    @advance_tag.setter
    def advance_tag(self, val):
        self[self.advance_mark_parameter_name] = val

    @property
    def system_tag(self):
        par = self.get_param(self.system_mark_parameter_name).AsString()
        return par if par else ""

    @system_tag.setter
    def system_tag(self, val):
        self.get_param(self.system_mark_parameter_name).Set(val)

    @property
    def length(self):
        par = self.get_param("Длина").AsDouble()
        return par if par else 0

    # Эта часть относится к остальным плагинам
    def set_windows_to_panel(self):
        all_holes = {}
        for i in self.windows:
            i = i.hole_parameter
            all_holes.setdefault(i, 0)
            all_holes[i] += 1
        res = ""
        elem_count = len(all_holes.items())
        for key, i in all_holes.items():
            elem_count -= 1
            if i == 1:
                res += key
            elif i > 1:
                res += "{} ({} шт.)".format(key, i)
            if elem_count > 0:
                res += ", "
        for i in self.element.GetParameters("BDS_Hole"):
            i.Set(res)

    def join_units_and_windows_to_panel(self):
        for i in self.units:
            self.join_elements([self], i.subcomponents)
        self.join_elements([self], [i for i in self.windows])


    # Эта часть для выгрузки в колористику
    def make_old_format(self, result, old_format_path):
        # echo(to_old_format)
        dir_path = old_format_path
        panel = result["value"]
        old_format = {
            "mark": [panel["mark"]],
            "components": panel["components"]["componentVals"],
            "details": panel["details"],
            "series": panel["series"]
        }
        for i in self.windows:
            old_format["components"].append(i.to_old_format())
        try:
            string = json.dumps(old_format, sort_keys=True,
                                indent=4, ensure_ascii=False)
            string = string.replace('"Body"', '"body"')
            string = string.replace('"Window"', '"window"')
            string = string.replace('"Connection"', '"connection"')
            string = string.replace('"Balcony"', '"window"')
            string = string.replace('"x"', '"X"')
            string = string.replace('"y"', '"Y"')
            string = string.replace('"z"', '"Z"')
            self.request_to_coloristic_server(json.loads("[" + string + "]"))
        except:
            echo("{} не выгружена в базу колористики".format(self))
            pass

    def get_mark_from_server(self, panel):
        "Получить марку с сервиса."
        pass

    def request_to_coloristic_server(self, parameters, action_type=r"/panelsstage/Precast/v1/Panels/createPanel"):
        """
        Запрос в сервис колористики для создания панели.
        """
        parameters = json.dumps(parameters).replace('"', '\"')
        headers = {
            "Content-type": "application/json",
            "Accept": "application/json"
        }
        conn = httplib.HTTPConnection(self.COLORISTIC_URI)
        conn.request("POST", action_type, parameters, headers)
        # echo(self.COLORISTIC_URI, action_type)
        response = conn.getresponse()
        return response.read().decode("utf-8")

    def add_ifc_parameter(self):
        """
        Добавление параметров локации к элементам для выгрузки в IFC

        Добавляются параметры для

        Платиков, закладных, окон и самой панели.

        Следующие параметры:
        BasisX
        BasisY
        BasisZ
        IsTransation
        Origin
        PanelId
        BoundingMin
        BoundingMax
        """
        all_elements = self.platics + \
            self.embedded_parts + self.windows + [self]

        for elem in all_elements:
            bb = elem.union_solid.GetBoundingBox()
            tt = bb.Transform
            bb_point_min = tt.OfPoint(bb.Min)
            bb_point_max = tt.OfPoint(bb.Max)
            trans = elem.element.GetTotalTransform()
            obj = {
                "BasisX": self.make_xyz(trans.BasisX, to_mm=False),
                "BasisY": self.make_xyz(trans.BasisX, to_mm=False),
                "BasisZ": self.make_xyz(trans.BasisX, to_mm=False),
                "Origin": self.make_xyz(trans.Origin),
                "BoundingMin": self.make_xyz(bb_point_min),
                "BoundingMax": self.make_xyz(bb_point_max),
                "IsTransation": trans.IsTranslation,
                "PanelId": self.Id
            }
            obj = json.dumps(obj, sort_keys=True, indent=4, ensure_ascii=False)
            elem["IFC_Export"] = obj

    def make_assambly(self):
        """
        Создать сборку из панели и всех ее компонентов.
        """
        cat = self.doc.Settings.Categories.get_Item(BuiltInCategory.OST_Walls).Id
        els = List[ElementId]()
        els.Add(self.element.Id)
        for i in self.windows:
            els.Add(i.element.Id)
            # echo(i)
        for i in self.embedded_parts:
            els.Add(i.element.Id)
        assambly = AssemblyInstance.Create(self.doc, els, cat)
        view = AssemblyViewUtils.Create3DOrthographic(self.doc, assambly.Id)
        view.get_Parameter(BuiltInParameter.MODEL_GRAPHICS_STYLE).Set(4)
        return assambly

    @property
    def assembly(self):
        if self.element.AssemblyInstanceId != ElementId.InvalidElementId:
            return self.doc.GetElement(self.element.AssemblyInstanceId)

    def disassemble(self):
        "Разобрать сборку, если элемент в сборке."
        if self.assembly:
            self.assembly.Disassemble()