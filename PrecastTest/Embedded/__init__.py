# -*- coding: utf-8 -*-
from ..Common import Precast_component
import json


class Precast_embedded_part(Precast_component):
    "Закладные детали."
    URI = 'vpp-map01'
    tag_parameter_name = "BDS_Tag"

    def __init__(self, element, doc=None, panel=None, analys_geometry=False):
        "Инициализация закладных деталей."
        self.analys_geometry = analys_geometry
        self.panel = panel
        self.doc = doc
        self.element = element
        js = self["JSON"]
        if js:
            js.Set(json.dumps(self.define_json()))

    def __repr__(self):
        return "Закладная id {} с BDS_Tag {}".format(
            self.element.Id.IntegerValue, self.tag)

    @property
    def point(self):
        if not hasattr(self, "_point"):
            point = self.element.Location.Point
            self.kostil = False
            if self.element.Symbol.Family.Name.startswith("352_Пластина"):
                self.kostil = True
                point += self.element.HandOrientation * \
                    self.element.LookupParameter("Рзм.Длина").AsDouble() / 2
                point += self.element.FacingOrientation * \
                    self.element.LookupParameter("Рзм.Ширина").AsDouble() / 2
            self._point = self.panel.transform.Inverse.OfPoint(
                point) - self.panel.ut_point
        return self._point

    @property
    def tag(self):
        par = self.get_param(self.tag_parameter_name)
        if par:
            return par.AsString()
        return ""

    def define_json(self):
        obj = {
            "type": "Connection",
            "name": self.tag,
            "point": self.make_xyz(self.point),
            "angle": 0,
            "group": None
        }
        return obj

    @property
    def mesure(self):
        w = self.get_param("Рзм.Ширина")
        h = self.element.LookupParameter("Рзм.Длина")
        t = self.element.LookupParameter("Рзм.Толщина")
        res_str = ""
        if w:
            res_str += str(w.AsDouble() * 304.8)
        if h:
            res_str += "x" + str(h.AsDouble() * 304.8)
        if t:
            res_str += "x" + str(t.AsDouble() * 304.8)
        res_str += " Расположен на отметке {}".format(round(self.point.Z * 304.8, 2))
        res_str += " с костылём" if self.kostil else ""
        return res_str
