# -*- coding: utf-8 -*-
from common_scripts import echo
from Autodesk.Revit.DB import XYZ
import json
from ..Common import Precast_component
from ..Common.Precast_json_template import Precast_json_template
from .Precast_window_validate import Precast_window_validate
from Precast.Common.Precast_validator import Precast_validator
from common_scripts.line_print import Line_printer
import httplib
import urllib


class Precast_window(Precast_component, Precast_window_validate, Precast_json_template):
    "Окна сборных конструкций."
    URI = 'vpp-map01'
    profile_server_path = "/v1/Component/find"

    def __init__(self, element, doc=None, panel=None, analys_geometry=False, develop=False):
        "Инициализация окна."
        super(Precast_window, self).__init__(element, doc, analys_geometry=analys_geometry, parent=panel)
        self.develop = develop
        self.element = element
        self.parent = panel
        # Сюда нужно будет потом записать Id который вернулся с сервера
        self.server_id = 0
        # Это непонятно зачем. Нужно переделать get_parameter
        self.el_type = self.element.Symbol
        self.error_message = ""
        self.parent.add_child(self)

        
        if self.is_valid:
            if self.analys_geometry and self.parent.is_analysed:
                if self.json:
                    json_par = self.prepare_json(self.json)
                    # echo(json_par)
                    if self.develop:
                        self.element.LookupParameter("JSON").Set(json_par)
                    result = self.UrlOpen(self.URI, parameters=json_par)
                    if "exception" in result.keys():
                        echo("{} exception с сервера \"{}\"".format(
                            self, result["exception"]["Message"]))
                        pass
                    elif "errors" in result.keys():
                        echo("{} errors с сервера \"{}\"".format(
                            self, result["errors"]))
                    else:
                        self.server_window_obj = result
                        self.server_id = result["id"]
        else:
            echo(self.error_message)

    def prepare_json(self, json_par):
        # echo(json_par)
        point = self.make_xyz(self.make_real_point())
        obj = json.loads(json_par)
        gen_obj = {
            "point": {
                "x": 0,
                "y": 0,
                "z": 0
            },
            "type": "Window" if point["z"] >= 400 else "Balcony",
            "solids": obj,
            "length": 0
        }
        return json.dumps(gen_obj)

    def to_old_format(self):
        point = self.make_xyz(self.make_real_point())
        old_window = {
            "point": point,
            "type": "Window" if point["z"] >= 300 else "Balcony",
            "solids": [],
            "lispWinId": None,
            "lispProfName": None
        }
        width = self.get_param("Рзм.Ширина").AsDouble() * 304.8
        for solid in self.server_window_obj["solids"]:
            right = [{"x": width + i["x"], "y": i["y"], "z": i["z"]}
                     for i in solid["right"]]
        #     old_window["solids"].a
            right.reverse()
            res = solid["left"] + right
            res = res[1:] + [res[0]]
            res.reverse()
            cursolid = {
                "plan": res,
                "profile": solid["profile"],
                "point": solid["point"],
                "layer": solid["layer"],
                "cutting": True
            }
            old_window["solids"].append(cursolid)
        return old_window

    def UrlOpen(self, uri, parameters=None):
        # params = parameters
        # params = urllib.urlencode(parameters)
        headers = {
            "Content-type": "application/json",
            "Accept": "application/json"
        }
        parameters = parameters.replace('"', '\"')
        # echo(parameters)
        conn = httplib.HTTPConnection(uri)
        parameters = parameters.encode("utf-8")
        conn.request("POST", self.profile_server_path, parameters, headers)
        response = conn.getresponse()
        return json.loads(response.read().decode("utf-8"))

    def __repr__(self):
        if self.server_id:
            return "Окно ser_id {}".format(self.server_id)
        return "Окно rev_id {}".format(self.element.Id.IntegerValue)

    @property
    def start_point(self):
        "Точка вставки."
        if not hasattr(self, "_start_point"):
            self._start_point = self.element.Location.Point
            # Line_printer.print_arc(self._start_point, radius=0.1)
        return self._start_point

    def make_real_point(self):
        if not hasattr(self, "_real_point"):
            vx = self.parent.vect_abscis
            vy = self.parent.vect_ordinat
            vz = self.parent.vect_applicat
            t = self.parent.get_param("BDS_Thickness").AsDouble() / 304.8
            point = self.start_point - t * vx - (self.width / 2) * vy
            point = self.parent.transform.Inverse.OfPoint(
                point) - self.parent.ut_point
            self._real_point = point
        return self._real_point

    @property
    def width(self):
        return self.get_param("Рзм.Ширина").AsDouble()

    def define_json(self):
        obj = {
            "point": self.make_xyz(self.make_real_point()),
            "length": int(self.width * 304.8),
            "id": self.server_id
        }
        return obj

    def get_parameter(self, parameter, is_type=True):
        "Получить параметр."
        if not hasattr(self, "params"):
            self._params = {}
        if parameter not in self._params.keys():
            if is_type:
                par = self.el_type.LookupParameter(parameter)
            else:
                par = self.element.LookupParameter(parameter)
            if par:
                par = par.AsDouble()
            else:
                par = 0
            self._params["parameter"] = par
        else:
            par = self._params["parameter"]
        return par

    @property
    def hole_parameter(self):
        # Параметр необходим, для заполнения BDS_Hole у панели
        w = self["Рзм.Ширина"]
        h = self["Рзм.Высота"]
        return "{}x{}".format(int(w), int(h))

    @property
    def mesure(self):
        w = round(self["Рзм.Ширина"], 2)
        h = round(self["Рзм.Высота"], 2)
        z = round(self.make_real_point().Z * 304.8, 2)
        res_str = "   {}x{} подоконник {}".format(w, h, z)
        return res_str
