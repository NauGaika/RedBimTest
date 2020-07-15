# -*- coding: utf-8 -*-
from Autodesk.Revit.DB import BoundingBoxIntersectsFilter, FilteredElementCollector, Outline, FamilyInstance
from Autodesk.Revit.DB import BooleanOperationsUtils, BooleanOperationsType, SetComparisonResult, IntersectionResultArray, BoundingBoxIsInsideFilter
from Autodesk.Revit.DB import Line, SolidCurveIntersectionOptions, XYZ, CurveLoop, BuiltInCategory, Solid, GeometryInstance, BooleanOperationsUtils, BooleanOperationsType
# from clr import StrongBox
from ..Window import Precast_window
from ..Embedded import Precast_embedded_part
from ..Unit import Precast_unit
from ..Hole.Precast_hole import Precast_hole
from ..Unit_member import Precast_unit_member
from common_scripts import echo
from common_scripts.line_print import Line_printer


class Precast_panel_finder(object):

    @property
    def windows(self):
        """
        Находим окна данной панели

        Нужно проверить является ли окно частью панели.
        Сейчас такой проверки нет
        """
        if not hasattr(self, "_windows"):
            bb = self.union_solid.GetBoundingBox()
            tt = bb.Transform
            p1 = tt.OfPoint(bb.Min)
            p2 = tt.OfPoint(bb.Max)
            v = (p2 - p1).Normalize()
            width = self.get_param("BDS_Thickness").AsDouble() / 304.8
            p1 += v * width * 2
            p2 -= v * width * 2
            outline = Outline(p1, p2)
            filtered = BoundingBoxIntersectsFilter(Outline(p1, p2))
            collector = FilteredElementCollector(self.doc).OfClass(
                FamilyInstance).WherePasses(filtered).ToElements()
            self._windows = [Precast_window(i, self.doc, self, analys_geometry=self.analys_geometry) for i in collector if i.Symbol.Family.Name[:len(
                self.windows_prefix)] == self.windows_prefix]
        return self._windows

    @property
    def holes(self):
        if not hasattr(self, "_holes"):
            bb = self.element.Geometry[self._default_option].GetBoundingBox()
            filtered = BoundingBoxIntersectsFilter(Outline(bb.Min, bb.Max))
            collector = FilteredElementCollector(self.doc).WherePasses(
                filtered).OfClass(FamilyInstance).ToElements()
            self._holes = [Precast_hole(i, self.doc, self) for i in collector if i.Symbol.Family.Name[:len(
                self.holes_prefix)] == self.holes_prefix]
        return self._holes

    @property
    def units(self):
        """
        Находим окна данной панели

        Нужно проверить является ли окно частью панели.
        Сейчас такой проверки нет
        """
        if not hasattr(self, "_units"):
            bb = self.union_solid.GetBoundingBox()
            tt = bb.Transform
            p1 = tt.OfPoint(bb.Min)
            p2 = tt.OfPoint(bb.Max)
            outline = Outline(p1, p2)
            filtered = BoundingBoxIntersectsFilter(outline)
            collector = FilteredElementCollector(self.doc).WherePasses(
                filtered).OfCategory(BuiltInCategory.OST_GenericModel).ToElements()
            res = []
            for i in collector:
                param = i.LookupParameter(self.element_type_parameter_name)
                param = param if param else i.Symbol.LookupParameter(self.element_type_parameter_name)
                if param and param.AsDouble() == self.unit_parameter_value:
                    res.append(Precast_unit.create(i, self.doc, self))
            self._units = res
        return self._units

    @property
    def embedded_parts(self):
        """
        Находим окна данной панели

        Нужно проверить является ли окно частью панели.
        Сейчас такой проверки нет
        """
        if not hasattr(self, "_embedded_parts"):
            bb = self.union_solid.GetBoundingBox()
            tt = bb.Transform
            p1 = tt.OfPoint(bb.Min)
            p2 = tt.OfPoint(bb.Max)
            outline = Outline(p1, p2)
            filtered = BoundingBoxIntersectsFilter(outline)
            collector = FilteredElementCollector(self.doc).OfCategory(
                BuiltInCategory.OST_Rebar).WherePasses(filtered)
            collector.UnionWith(FilteredElementCollector(self.doc).OfCategory(
                BuiltInCategory.OST_StructuralFraming).WherePasses(
                filtered)).ToElements()
            res = []
            for i in collector:
                param = i.LookupParameter(self.element_type_parameter_name)
                if param and param.AsDouble() == self.embedded_part_parameter_value:
                    # if self.is_element_of_supercomponent(i):
                        res.append(Precast_embedded_part(i, self.doc, self))
            self._embedded_parts = res
        return self._embedded_parts

    @property
    def platics(self):
        """
        Платики.
        Ищем платики данной панели.
        """
        if not hasattr(self, "_platics"):
            bb = self.union_solid.GetBoundingBox()
            tt = bb.Transform
            p1 = tt.OfPoint(bb.Min)
            p2 = tt.OfPoint(bb.Max)
            outline = Outline(p1, p2)
            filtered = BoundingBoxIntersectsFilter(outline)
            collector = FilteredElementCollector(self.doc).OfCategory(
                BuiltInCategory.OST_StructConnections).WherePasses(filtered)
            collector = collector.ToElements()
            res = []
            for i in collector:
                param = i.LookupParameter(self.element_type_parameter_name)
                param = i.Symbol.LookupParameter(self.element_type_parameter_name) if param is None else param
                if param and param.AsDouble() == self.platic_parameter_value:
                    res.append(Precast_unit_member(i, self.doc, self))
            self._platics = res
        return self._platics

    def is_element_of_supercomponent(self, element):
        if element.SuperComponent:
            sup = element.SuperComponent
            if sup.Id.IntegerValue == self.element.Id.IntegerValue:
                return True
            elif sup.SuperComponent:
                return self.is_element_of_supercomponent(sup)

    def is_intersect_solids(self, element):
        all_element_dict = []
        geom = element.Geometry[self._default_option]
        for i in geom:
            if isinstance(i, Solid):
                all_element_dict.append(i)
            elif isinstance(i, GeometryInstance):
                all_element_dict += [j for j in list(
                    i.GetInstanceGeometry()) if isinstance(j, Solid)]
        res = False
        for i in all_element_dict:
            for k in self.solids:
                j = k.element
                new_solid = BooleanOperationsUtils.ExecuteBooleanOperation(
                    i, j, BooleanOperationsType.Union)
                is_intersect = round((new_solid.SurfaceArea - i.SurfaceArea - j.SurfaceArea) + (
                    new_solid.Volume - i.Volume - j.Volume), 5) != 0
                if is_intersect:
                    return True
