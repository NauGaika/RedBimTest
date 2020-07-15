# -*- coding: utf-8 -*-
import json
import httplib
import urllib
import math
from common_scripts import echo
from Autodesk.Revit.DB import Family, FilteredElementCollector, BuiltInParameter, ElementId, XYZ, Line, ElementTransformUtils, Plane
from Autodesk.Revit.DB.Structure import StructuralType
from ..Window import Precast_window
from ..Panel import Precast_panel


class PrecastPanelCreator(object):
    default_panel_family_name = "215_Панель наружная (Стены_ТипМод)"
    default_window_family_name = "221_Окно_Контейнер"
    default_panel_type_name = "Тип 1"
    URI = 'vpp-map01'
    panel_server_path = "/v1/Panel/"
    all_windows = {
        17: ("Рядовое h=2378", "all"),
        21: ("Угловое h=2000", "left"),  # левое
        20: ("Угловое h=2000", "right"),  # правое
        19: ("Угловое прямое h=2000", "left"),  # левое
        18: ("Угловое прямое h=2000", "right"),  # правое
        12: ("Рядовое h=2000", "all")
    }

    @property
    def default_panel_family(self):
        """Получаем семейство панели по умолчанию."""
        if not hasattr(self, "_default_panel_family"):
            self._default_panel_family = FilteredElementCollector(self.doc).\
                OfClass(Family).ToElements()
            for i in self._default_panel_family:
                if i.Name == self.default_panel_family_name:
                    self._default_panel_family = i
                    break
        return self._default_panel_family

    @property
    def default_panel_type(self):
        """Получаем тип панели по умолчанию."""
        if not hasattr(self, "_default_panel_type"):
            dpt = self.default_panel_family.GetFamilySymbolIds()
            dpt = [self.doc.GetElement(i) for i in dpt]
            for i in dpt:
                if i.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).\
                        AsString() == self.default_panel_type_name:
                    self._default_panel_type = i
                    break
        return self._default_panel_type

    @property
    def window_family(self):
        if not hasattr(self, "_window_family"):
            self._window_family = FilteredElementCollector(self.doc).\
                OfClass(Family).ToElements()
            for i in self._window_family:
                if i.Name == self.default_window_family_name:
                    self._window_family = i
            element_types = {}
            dpt = self._window_family.GetFamilySymbolIds()
            dpt = [self.doc.GetElement(i) for i in dpt]
            dpt = {i.get_Parameter(
                BuiltInParameter.SYMBOL_NAME_PARAM).AsString(): i for i in dpt}
            self._window_family = dpt
        return self._window_family

    @property
    def default_level(self):
        return self.doc.GetElement(ElementId(1610))

    def __init__(self, revit):
        self.__revit__ = revit
        self.doc = revit.ActiveUIDocument.Document

    def create_test_panel(self):
        """
        Создать тестовую панель.
        """
        # echo(self.default_panel_type)
        self.element = self.doc.Create.NewFamilyInstance(
            XYZ(0, 0, 0), self.default_panel_type, self.default_level, StructuralType.Column)
        self.element = Precast_panel(self.element)
        params = {"marks": ["3НСКг-[100.СБП]-513.324.36-141.1"]}
        self.element_dict = json.loads(self.find_panels_on_server(
            parameters=params, action_type="filter"))[0]
        self.element_params = self.get_parameter_from_dict(self.element_dict)
        self.element["Длина"] = self.element_params["Длина"] / 304.8
        self.element["BDS_LeftEndType"] = self.element_params["Угол_тип_левый"]
        self.element["BDS_RightEndType"] = self.element_params["Угол_тип_правый"]
        self.create_widnow_for_panel(self.element_dict, self.element_params, panel=self.element)

    def create_widnow_for_panel(self, panel_dict, panel_params, panel=None):
        """
        Создать окна в панели.
        """
        for i in panel_dict['components']['componentRefs']:
            window_type = self.all_windows[i["id"]]
            symb = self.window_family[window_type[0]]
            add_point = XYZ(i['point']['x'], i['point']['y'], i['point']['z']) / 304.8
            c_window = self.doc.Create.NewFamilyInstance(
                add_point,
                symb,
                self.default_level,
                StructuralType.Column)
            c_window = Precast_window(c_window, doc=self.doc, panel=panel)
            c_window["Рзм.Ширина"] = i["length"] / 304.8
            new_point = c_window.element.Location.Point
            new_point = new_point + XYZ(i["length"] / 304.8 / 2, 0, 0)
            # new_point = new_point + XYZ(i["length"] / 304.8 / 2, 0, 0)
            c_window.element.Location.Point = new_point
            axis = Line.CreateBound(c_window.element.Location.Point, c_window.element.Location.Point + XYZ(0,0,10))
            c_window.element.Location.Rotate(axis, math.pi)
            if window_type[1] == "left":
                plane = Plane.CreateByNormalAndOrigin(XYZ(1,0,0), c_window.element.Location.Point)
                new_win = ElementTransformUtils.MirrorElement(self.doc, c_window.element.Id, plane)

                self.doc.Delete(c_window.element.Id)
                # c_win = Precast_window(new_win, doc=self.doc, panel=panel)
            # c_window.element.Location.Rotation = math.pi

    def get_parameter_from_dict(self, panel):
        parameters = {}
        parameters['Толщина'] = 0
        parameters['Длина'] = 0
        parameters['Высота'] = 0
        for i in panel['components']['componentVals']:
            for solid in i["solids"]:
                min_v = {"x": float('inf'), "y": float(
                    'inf'), "z": float('inf')}
                max_v = {"x": float('-inf'), "y": float('-inf'),
                         "z": float('-inf')}
                for k in ["plan", "profile"]:
                    for point in solid[k]:
                        for key, val in point.items():
                            if min_v[key] > val:
                                min_v[key] = val
                            if max_v[key] < val:
                                max_v[key] = val
                _lenght = max_v['x'] - min_v['x']

                if _lenght > parameters['Длина']:
                    parameters['Длина'] = _lenght

                if max_v['z'] > parameters['Высота']:
                    parameters['Высота'] = max_v['z']

                if solid['layer'] == 1:
                    parameters["Толщина_внутренний"] = max_v['y']
                elif solid['layer'] == 2:
                    parameters["Толщина_утеплитель"] = max_v['y']
                if solid['layer'] == 3:
                    parameters["Толщина_внешний"] = max_v['y']
                if solid['layer'] == 4:
                    parameters["Толщина_отделка"] = max_v['y']

                parameters['Толщина'] += max_v['y']
        for i in panel['components']['componentVals']:
            left_type = 0
            right_type = 0
            sec_right = 0
            sec_left = 0
            for solid in i["solids"]:
                left_count = 0
                right_count = 0
                for point in solid["plan"]:
                    is_right = point['x'] < parameters["Длина"] / 2
                    if is_right:
                        right_count += 1
                        c_x = point["x"]
                    else:
                        left_count += 1
                        c_x = parameters["Длина"] - point["x"]
                    if solid['layer'] == 1 and c_x > 0 and is_right:
                        sec_right = 2
                    if solid['layer'] == 1 and c_x > 0 and not is_right:
                        sec_left = 2
                if left_count == 4:
                    left_type = 1
                else:
                    left_type = sec_left
                if right_count == 4:
                    right_type = 1
                else:
                    right_type = sec_right
        parameters["Угол_тип_левый"] = left_type
        parameters["Угол_тип_правый"] = right_type
        return parameters

    def find_panels_on_server(self, parameters=None, action_type="find"):
        """
        Метод отправляет запрос на сервер для поиска панели.

        Передавать нужно parameters - массив
        action_type - действие, которое нуно выполнить
        """
        parameters = json.dumps(parameters).replace('"', '\"')
        headers = {
            "Content-type": "application/json",
            "Accept": "application/json"
        }
        conn = httplib.HTTPConnection(self.URI)
        conn.request("POST", self.panel_server_path +
                     action_type, parameters, headers)
        response = conn.getresponse()
        return response.read().decode("utf-8")

    def get_param(self, param, fam=None):
        """
        Метод получения параметров из семейства.

        По умолчанию берется параметр у текущего элемента.

        fam - нужно убрать.
        """
        # echo(param)
        if not hasattr(self, "_all_parameters"):
            self._all_parameters = {}
        if param not in self._all_parameters.keys():
            par = self.element.LookupParameter(param)
            if not par:
                par = self.element.Symbol.LookupParameter(param)
            self._all_parameters[param] = par
        return self._all_parameters[param]

    def __getitem__(self, key):
        """
        Получение параметра на основании имени параметра по индексу.

        Проверяется тип параметра и в зависимости от этого
        возвращается значение приведенное к метрическим значениям

        Если параметр не найдет - возвращается None
        """
        par = self.get_param(key)
        if par:
            if par.Definition.ParameterType == ParameterType.Number:
                return par.AsDouble()
            elif par.Definition.ParameterType == ParameterType.Text:
                return par.AsString()
            elif par.Definition.ParameterType == ParameterType.Integer:
                return par.AsInteger()
            elif par.Definition.ParameterType == ParameterType.Length:
                return par.AsDouble() * 304.8
            elif par.Definition.ParameterType == ParameterType.Area:
                return par.AsDouble() * (304.8**2)
            elif par.Definition.ParameterType == ParameterType.Volume:
                return par.AsDouble() * (304.8**3)
            elif par.Definition.ParameterType == ParameterType.Invalid:
                return par.AsValueString()

    def __setitem__(self, key, val):
        """
        Установка значения параметра по индексу.
        Если параметр не найдет
        """
        par = self.get_param(key)
        if par:
            par.Set(val)
        else:
            raise Exception("Параметр {} не найден у {}".format(key, self))
