# coding: utf8
"""Модуль по работе с поверхностями"""

import clr
from copy import copy
from common_scripts import echo
# from math import pi
from Autodesk.Revit.DB import GeometryCreationUtilities, UV, Options, GeometryInstance, Solid, IntersectionResultArray,\
                              FaceIntersectionFaceResult, PlanarFace, SetComparisonResult, XYZ, Line
from common_scripts.line_print import Line_printer
from common_scripts.vector_math import rotate_point_by_axec


class RB_Face:
    """Работа с поверхностями."""

    @classmethod
    def find_common_face(cls, elem1, elem2):
        """Ищет общие поверхности."""
        faces1 = cls.get_faces_from_solid(elem1)
        faces2 = cls.get_faces_from_solid(elem2)
        result = []
        for face1 in faces1:
            for face2 in faces2:
                if isinstance(face1, PlanarFace) and isinstance(face2, PlanarFace):
                    lines = list(face2.GetEdgesAsCurveLoops())[0]
                    add_elem = True
                    for line in lines:
                        res = face1.Intersect(line, clr.StrongBox[IntersectionResultArray]())
                        if res != SetComparisonResult.Subset:
                            add_elem = False
                    if add_elem:
                        result.append(face2)
        return result

    @classmethod
    def get_faces_from_solid(cls, elem):
        """Возвращает все поверхсти элемента."""
        option = Options()
        faces = []
        geometry = elem.get_Geometry(option)
        for geometry_intance in geometry:
            if isinstance(geometry_intance, Solid):
                faces += list(geometry_intance.Faces)
        return faces
