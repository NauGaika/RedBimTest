# -*- coding: utf-8 -*-
from ..Common.Precast_geometry import Precast_geometry
from common_scripts import echo
from Autodesk.Revit.DB import XYZ
# import json
# from .Precast_analys_geometry import Precast_analys_geometry
from common_scripts.line_print import Line_printer


class Precast_hole(Precast_geometry):
    "Окна сборных конструкций."

    def __init__(self, hole, doc, parent=None, analys_geometry=False):
        self.analys_geometry = analys_geometry
        self.element = hole
        self.doc = doc
        self.parent = parent
        self.el_type = self.element.Symbol
        self.define_json()

    def __repr__(self):
        return "Отверстие id {}".format(self.element.Id.IntegerValue)

    @property
    def start_point(self):
        "Точка вставки."
        if not hasattr(self, "_start_point"):
            self._start_point = self.element.Location.Point
        return self._start_point


    def get_parameter(self, parameter, is_type=True, to_mm=True):
        "Получить параметр."
        if is_type:
            par = self.el_type.LookupParameter(parameter)
        else:
            par = self.element.LookupParameter(parameter)
        if par:
            par = par.AsDouble() * (304.8 * to_mm + 1 - to_mm) 
        else:
            par = 0
        return par

    def define_json(self):
        "Json Описание окна"
        # Line_printer.print_arc(self.start_point)

        t_1 = self.get_parameter("1_Толщина", to_mm=False)
        t_2 = self.get_parameter("2_Толщина", to_mm=False)
        t_3 = self.get_parameter("3_Толщина", to_mm=False)
        t_4 = self.get_parameter("4_Толщина", to_mm=False)
        ot_b_4 = self.get_parameter("4_Отступ_низ", to_mm=False)
        height = self.get_parameter("Рзм.Высота",  is_type=False, to_mm=False)
        width = self.get_parameter("Рзм.Ширина", to_mm=False,  is_type=False)
        vx = XYZ(1, 0, 0)# self.parent.vect_abscis
        vy = XYZ(0, 1, 0)# self.parent.vect_ordinat
        vz = self.parent.vect_applicat
        point = self.parent.transform.Inverse.OfPoint(self.start_point) - self.parent.ut_point + vx * width / 2 - (t_1 + t_2 + t_3 + t_4) * vy

        l_4_p = (vz * ot_b_4)
        l_4_p_1_1 = XYZ()
        l_4_p_2_1 = l_4_p_1_1 + width * vx
        l_4_p_3_1 = l_4_p_2_1 + height * vz
        l_4_p_4_1 = l_4_p_3_1 - width * vx
        l_4_p_1_2 = l_4_p_1_1 + t_4 * vy
        l_4_p_2_2 = l_4_p_2_1 + t_4 * vy
        l_4_p_3_2 = l_4_p_3_1 + t_4 * vy
        l_4_p_4_2 = l_4_p_4_1 + t_4 * vy

        l_3_p = (vz * ot_b_4) + t_4 * vy
        l_3_p_1_1 = XYZ()
        l_3_p_2_1 = l_3_p_1_1 + width * vx
        l_3_p_3_1 = l_3_p_2_1 + height * vz
        l_3_p_4_1 = l_3_p_3_1 - width * vx
        l_3_p_1_2 = l_3_p_1_1 + t_3 * vy
        l_3_p_2_2 = l_3_p_2_1 + t_3 * vy
        l_3_p_3_2 = l_3_p_3_1 + t_3 * vy
        l_3_p_4_2 = l_3_p_4_1 + t_3 * vy

        l_2_p = (vz * ot_b_4) + (t_4 + t_3) * vy
        l_2_p_1_1 = XYZ()
        l_2_p_2_1 = l_2_p_1_1 + width * vx
        l_2_p_3_1 = l_2_p_2_1 + height * vz
        l_2_p_4_1 = l_2_p_3_1 - width * vx
        l_2_p_1_2 = l_2_p_1_1 + t_2 * vy
        l_2_p_2_2 = l_2_p_2_1 + t_2 * vy
        l_2_p_3_2 = l_2_p_3_1 + t_2 * vy
        l_2_p_4_2 = l_2_p_4_1 + t_2 * vy

        l_1_p = (t_4 + t_3 + t_2) * vy
        l_1_p_1_1 = XYZ()
        l_1_p_2_1 = l_1_p_1_1 + width * vx
        l_1_p_3_1 = l_1_p_2_1 + height * vz
        l_1_p_4_1 = l_1_p_3_1 - width * vx
        l_1_p_1_2 = l_1_p_1_1 + t_1 * vy
        l_1_p_2_2 = l_1_p_2_1 + t_1 * vy
        l_1_p_3_2 = l_1_p_3_1 + t_1 * vy
        l_1_p_4_2 = l_1_p_4_1 + t_1 * vy
        
        obj = {
            "type": "Cut",
            "solids": [
                self.make_layer(4, l_4_p, l_4_p_1_1, l_4_p_2_1, l_4_p_3_1, l_4_p_4_1, l_4_p_1_2, l_4_p_2_2, l_4_p_3_2, l_4_p_4_2),
                self.make_layer(3, l_3_p, l_3_p_1_1, l_3_p_2_1, l_3_p_3_1, l_3_p_4_1, l_3_p_1_2, l_3_p_2_2, l_3_p_3_2, l_3_p_4_2),
                self.make_layer(2, l_2_p, l_2_p_1_1, l_2_p_2_1, l_2_p_3_1, l_2_p_4_1, l_2_p_1_2, l_2_p_2_2, l_2_p_3_2, l_2_p_4_2),
                self.make_layer(1, l_1_p, l_1_p_1_1, l_1_p_2_1, l_1_p_3_1, l_1_p_4_1, l_1_p_1_2, l_1_p_2_2, l_1_p_3_2, l_1_p_4_2)
            ],
            "point": self.make_xyz(point)
        }
        return obj


    def make_layer(self, layer_number, point, p1_1, p2_1, p3_1, p4_1, p1_2, p2_2, p3_2, p4_2):
        "Создаем слой."
        obj = {
            "layer": layer_number,
            "point": self.make_xyz(p1_1),
            "plan": [
                self.make_xyz(p1_1, n_z=True),
                self.make_xyz(p2_1, n_z=True),
                self.make_xyz(p2_2, n_z=True),
                self.make_xyz(p1_2, n_z=True)
            ],
            "profile": [
                self.make_xyz(p1_1, n_x=True),
                self.make_xyz(p1_2, n_x=True),
                self.make_xyz(p4_2, n_x=True),
                self.make_xyz(p4_1, n_x=True)
            ],
            "cutting": True
        }
        return obj

    def make_xyz(self, point, to_mm=True, n_x=False, n_y=False, n_z=False):
        "Преобразовать XYZ() в dict."
        return {
            "x": int(round(point.X * (304.8 * to_mm + 1 - to_mm)) * (1 - n_x)),
            "y": int(round(point.Y * (304.8 * to_mm + 1 - to_mm)) * (1 - n_y)),
            "z": int(round(point.Z * (304.8 * to_mm + 1 - to_mm)) * (1 - n_z))
        }