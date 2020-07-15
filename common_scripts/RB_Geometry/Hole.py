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
            # Получить нормаль у плоскости, в которой лежит cl
            plane_normal = cl.GetPlane().Normal
            # Сформировать солид выдавливанием
            solid_elem = GeometryCreationUtilities.CreateExtrusionGeometry(
                [cl], plane_normal, 1)
            i_x = i_x + 1
            # Пройти по всем поверхностям полученного солида
            for face in solid_elem.Faces:
                # Если нормаль поверхности совпадает с нормалью cl - необходимая поверхность
                if face.FaceNormal.IsAlmostEqualTo(plane_normal):
                    all_cl_with_extrussion.append((
                        face,
                        cl,
                        i_x))

        for elem in all_cl_with_extrussion:
            # Проходим по всем полученным выдавливаниям
            outside = True
            for elem_2 in all_cl_with_extrussion:
                if not elem[2] == elem_2[2]:
                    # Если первая точка всех наборов cl не лежит на поверхности. cl внутренний
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
        # находим нормаль(производну)
        trans = e_2[0].ComputeDerivatives(UV(0, 0))
        # ПОлучаем точку на поверхносте
        Pt = trans.Inverse.OfPoint(first_point)
        # Находится ли точка внутри поверхности?
        res = e_2[0].IsInside(UV(Pt.X, Pt.Y))
        return res
