# -*- coding: utf-8 -*-
from .Precast_validator import Precast_validator
from .Precast_geometry import Precast_geometry
from Autodesk.Revit.DB import ParameterType


class Precast_component(Precast_validator, Precast_geometry):

    def __init__(self, element, doc, analys_geometry=None, parent=None):
        self.parent = parent
        self.children = set()
        self.element = element
        self.doc = doc
        self.transform = self.element.GetTransform()
        self.analys_geometry = analys_geometry
        self._default_option = self.__class__.option_medium
        super(Precast_component, self).__init__()

    def add_child(self, child):
        self.children.add(child)
        if self.parent:
            self.parent.add_child(child)

    @property
    def rotation(self):
        "Точка вставки."
        if not hasattr(self, "_rotation"):
            self._rotation = self.element.Location.Rotation
        return self._rotation

    @property
    def Id(self):
        if not hasattr(self, "_Id"):
            self._Id = self.element.Id.IntegerValue
        return self._Id

    def make_xyz(
            self,
            point, to_mm=True,
            upper=False,
            nullable_x=False, nullable_y=False,
            nullable_z=False, round_if_mm=1):
        "Преобразовать XYZ() в dict."
        arr = ["x", "y", "z"]
        vals = [point.X * (1 - nullable_x), point.Y *
                (1 - nullable_y), point.Z * (1 - nullable_z)]

        def func_1(x): return x * (304.8 * to_mm + 1 - to_mm)
        if to_mm:
            def func_2(x): return round(func_1(x), round_if_mm)
        else:
            func_2 = func_1
        if upper:
            arr = list(map(str.upper, arr))
        return {key: i for key, i in zip(arr, map(func_2, vals))}

    def get_param(self, param, fam=None):
        """
        Метод получения параметров из семейства.

        По умолчанию берется параметр у текущего элемента.
        Если передан параметр fam - берем этот параметр
        у fam.
        """
        if not hasattr(self, "_all_parameters"):
            self._all_parameters = {}
        if fam is None:
            if param not in self._all_parameters.keys():
                par = self.element.LookupParameter(param)
                if not par:
                    par = self.element.Symbol.LookupParameter(param)
                self._all_parameters[param] = par
            return self._all_parameters[param]
        else:
            par = fam.LookupParameter(param)
            par = par.Symbol.LookupParameter(param if par is None else par)
            return par

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

    @property
    def tag(self):
        """
        Марка элемента Геттер.
        """
        par = self[self.mark_parameter_name]
        return par if par else ""

    @tag.setter
    def tag(self, val):
        """
        Марка элемента Сеттер.
        """
        self[self.mark_parameter_name] = val
