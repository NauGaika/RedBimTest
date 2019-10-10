# coding: utf8
"""Работа с проемами геометрии."""

from common_scripts import echo
# from math import pi
from Autodesk.Revit.DB import GeometryCreationUtilities, UV


class Hole:
    """Работа с проемами геометрии."""

    @classmethod
    def find_outer_contur_in_cls(cls, curve_loops):
        """Ищет внешний контур."""
        all_cl_with_extrussion = []
        inner_cls = []
        outer_cls = []
        i_x = 0
        for cl in curve_loops:
            plane_normal = cl.GetPlane().Normal
            solid_elem = GeometryCreationUtilities.CreateExtrusionGeometry(
                [cl], plane_normal, 1)
            i_x = i_x + 1
            for face in solid_elem.Faces:
                if face.FaceNormal.IsAlmostEqualTo(plane_normal):
                    all_cl_with_extrussion.append((
                        face,
                        cl,
                        i_x))

        for elem in all_cl_with_extrussion:
            outside = True
            for elem_2 in all_cl_with_extrussion:
                if not elem[2] == elem_2[2]:
                    if cls.first_point_is_inside_face(elem, elem_2):
                        outside = False
                        break
            if outside:
                outer_cls.append(elem[1])
            else:
                inner_cls.append(elem[1])
        return (outer_cls, inner_cls)


    @classmethod
    def first_point_is_inside_face(cls, e_1, e_2):
        """Находится ли первая точка контура внутри поверхности."""
        first_point = list(e_1[1])[0].GetEndPoint(0)
        trans = e_2[0].ComputeDerivatives(UV(0, 0))
        Pt = trans.Inverse.OfPoint(first_point)
        res = e_2[0].IsInside(UV(Pt.X, Pt.Y))
        return res
