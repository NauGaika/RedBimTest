# -*- coding: utf-8 -*-
from Autodesk.Revit.DB import BooleanOperationsType, BooleanOperationsUtils
from Autodesk.Revit.DB import Options, ViewDetailLevel, Solid, XYZ, GeometryInstance, JoinGeometryUtils
from Autodesk.Revit.DB import Line, Plane, BuiltInCategory, Category
# from Autodesk.Revit.DB.Structure import Rebar
from Autodesk.Revit.Exceptions import InvalidOperationException
from .Precast_solid import Precast_solid
from common_scripts import echo


class Precast_geometry(object):
    "Примесь для поиска солидов."
    option_coarse = Options()
    option_coarse.DetailLevel = ViewDetailLevel.Coarse
    option_medium = Options()
    option_medium.DetailLevel = ViewDetailLevel.Medium
    option_fine = Options()
    option_fine.DetailLevel = ViewDetailLevel.Fine
    _default_option = option_medium

    def __init__(self):
        self._solids = None
        self._union_solid = None
        super(Precast_geometry, self).__init__()

    def get_solids(self, solids, res):
        "Записываем солиды и записываем в res рекурсивно."
        if solids:
            for i in solids:
                if isinstance(i, Solid):
                    res.append(Precast_solid(i, self.doc))
                if isinstance(i, GeometryInstance):
                    self.get_solids(i.GetInstanceGeometry(), res)

    @property
    def solids(self):
        "Все солиды элемента."
        if not hasattr(self, "_solids") or self._solids is None:
            self._solids = []
            solids = self.element.Geometry[self._default_option]
            self.get_solids(solids, self._solids)
        return self._solids

    @property
    def real_solids(self):
        "Все солиды элемента."
        if not hasattr(self, "_real_solids"):
            self._real_solids = []
            solids = self.element.Geometry[self.option_fine]
            self.get_solids(solids, self._real_solids)
        return self._real_solids

    @property
    def union_solid(self):
        "Объединение всех солидов."
        if not hasattr(self, "_union_solid") or self._union_solid is None:
            self._union_solid = None
            if self.solids:
                for i in self.solids:
                    if self._union_solid is None:
                        self._union_solid = i.element
                    else:
                        self._union_solid = BooleanOperationsUtils.ExecuteBooleanOperation(self._union_solid, i.element, BooleanOperationsType.Union)
        return self._union_solid

    def join_elements(self, elements_1, elements_2):
        "Присоединяет геометрию элементов"
        result = set()
        rebar_cat = Category.GetCategory(self.doc, BuiltInCategory.OST_Rebar).Name
        elements_1 = [i for i in elements_1 if i.element.Category.Name != rebar_cat]
        elements_2 = [i for i in elements_2 if i.element.Category.Name != rebar_cat]
        for element_1 in elements_1:
            for element_2 in elements_2:
                try:
                    res = BooleanOperationsUtils.ExecuteBooleanOperation(element_2.union_solid, element_1.union_solid, BooleanOperationsType.Difference)
                    if res.Volume < element_2.union_solid.Volume:
                        result.add(element_1)
                        try:
                            if not JoinGeometryUtils.AreElementsJoined(self.doc, element_2.element, element_1.element):
                                JoinGeometryUtils.JoinGeometry(self.doc, element_2.element, element_1.element)
                            if not JoinGeometryUtils.IsCuttingElementInJoin(self.doc, element_2.element, element_1.element):
                                JoinGeometryUtils.SwitchJoinOrder(self.doc, element_2.element, element_1.element)
                        except:
                            # echo("Ошибка в объединении {} с {}".format(element_1, element_2))
                            pass
                except InvalidOperationException:
                    result.add(element_1)
        return result


    @property
    def center_point(self):
        if not hasattr(self, "_center_point"):
            bb = self.element.Geometry[self._default_option].GetBoundingBox()
            delta = bb.Max - bb.Min
            delta = delta / 2
            self._center_point = bb.Min + delta
        return self._center_point

    @property
    def height(self):
        if not hasattr(self, "_height"):
            bb = self.element.Geometry[self._default_option].GetBoundingBox()
            delta = bb.Max - bb.Min
            self._height = delta.GetLength()
        return self._height

    @property
    def vect_abscis(self):
        "Ветор X."
        if not hasattr(self, "_vect_abscis"):
            self._vect_abscis = self.element.FacingOrientation
        return self._vect_abscis

    @property
    def vect_ordinat(self):
        "Ветор Y."
        if not hasattr(self, "_vect_ordinat"):
            self._vect_ordinat = self.element.HandOrientation
        return self._vect_ordinat

    @property
    def vect_applicat(self):
        "Ветор Z."
        if not hasattr(self, "_vect_applicat"):
            self._vect_applicat = XYZ(0, 0, 1)
        return self._vect_applicat

    @staticmethod
    def project_on_plane(point, origin=None, normal=None, plane=None):
        "Проекция точки на плоскость."
        if plane is None:
            plane = Plane.CreateByNormalAndOrigin(normal, origin)
        normal = plane.Normal * plane.Project(point)[1]
        return point - normal

    @classmethod
    def project_line_on_plane(cls, line, origin=None, normal=None, plane=None):
        p1 = line.GetEndPoint(0)
        p1 = cls.project_on_plane(p1, origin=origin, normal=normal, plane=plane)
        p2 = line.GetEndPoint(1)
        p2 = cls.project_on_plane(p2, origin=origin, normal=normal, plane=plane)
        # echo(p1.IsAlmostEqualTo(p2))
        if not p1.IsAlmostEqualTo(p2):
            try:
                return Line.CreateBound(p1, p2)
            except:
                pass