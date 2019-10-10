# coding: utf8
"""Работа поиском поверхностей"""

import clr
from copy import copy
from common_scripts import echo
# from math import pi
from Autodesk.Revit.DB import GeometryCreationUtilities, UV, Options, GeometryInstance, Solid, IntersectionResultArray,\
                              FaceIntersectionFaceResult, PlanarFace, SetComparisonResult, XYZ, Line
from common_scripts.line_print import Line_printer
from common_scripts.vector_math import rotate_point_by_axec

class RB_Face:
    iteration_count = 0
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
    def find_wall_direction_faces(cls, wall):
        """Ищем боковые поверхносит стены."""
        faces = cls.get_faces_from_solid(wall)
        direction = wall.Orientation
        result = []
        for face in faces:
            normal = face.ComputeNormal(UV(0, 0))
            if normal.IsAlmostEqualTo(direction) or normal.Negate().IsAlmostEqualTo(direction):
                result.append(face)
        return result
        # echo(direction)

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

    @classmethod
    def get_common_line_in_faces(cls, face_arr_1, face_arr_2):
        """Получаем две поверхности. Возвращаем общие грани и поверхности."""
        result = []
        for face_1 in face_arr_1:
            face_1_lines = cls.get_all_line_in_face(face_1)
            for face_2 in face_arr_2:
                face_2_lines = cls.get_all_line_in_face(face_2)
                for line in face_1_lines:
                    for line_2 in face_2_lines:
                        res = line.Intersect(line_2, clr.StrongBox[IntersectionResultArray]())
                        if res == SetComparisonResult.Equal:
                            result.append((face_1, face_2, line))
        return result

    @classmethod
    def get_all_line_in_face(cls, face):
        """Возвращает все грани данной поверхности."""
        cls = face.GetEdgesAsCurveLoops()
        all_line = []
        for cl in cls:
            for line in cl:
                all_line.append(line)
        return all_line

    @classmethod
    def get_charactep_points_in_face(cls, face):
        """
        Ищет все характерные точки на плоскости.

        Сейчас работает только с прямыми линиями.
        """
        cls = face.GetEdgesAsCurveLoops()
        u_set = set()
        v_set = set()
        for cl in cls:
            for line in cl:
                if isinstance(line, Line):
                    uv = face.Project(line.GetEndPoint(0)).UVPoint
                    u_set.add(uv.U)
                    v_set.add(uv.V)
        all_UV_points = set()
        for u in u_set:
            for v in v_set:
                all_UV_points.add(UV(u, v))
        return all_UV_points

    @classmethod
    def find_nearest_point_by_direction(cls, point, points, direction=0):
        """Находим ближайшую точку по направлению.

        direction
        0 - по вертикали
        1 - по горизонтали
        """
        gen_point = point
        if direction != 0:
            gen_point = UV(gen_point.V, gen_point.U)
        find_point = None
        for point in points:
            if direction != 0:
                temp_point = UV(point.V, point.U)
            else:
                temp_point = point
            if not gen_point.IsAlmostEqualTo(UV(gen_point.U, temp_point.V)):
                if temp_point.V > gen_point.V:
                    distance = gen_point.DistanceTo(temp_point)
                    if not find_point or find_point[1] > distance:
                        find_point = (temp_point, distance)
        if find_point:
            if direction != 0:
                return UV(find_point[0].V, find_point[0].U)
            return find_point[0]

    @classmethod
    def create_region_by_point(cls, points):
        """
        Создает регионы из точек. Прямоугольники с координатами левой верхней и правой нижней точки.

        Берем ближайшую правую точку и от нее берем ближайшую нижнюю точку
        """
        region = list()
        for point in points:
            h_point = cls.find_nearest_point_by_direction(point, points, direction=0)
            if h_point:
                v_point = cls.find_nearest_point_by_direction(h_point, points, direction=1)
                if v_point:
                    region.append((point, v_point))
        return region

    @classmethod
    def find_hole_region(cls, face, regions):
        """Определяет является ли регион отверстием."""
        region_with_hole = list()
        for region in regions:
            center = (region[1] - region[0]) / 2 + region[0]
            region_with_hole.append((region[0], region[1], not face.IsInside(center)))
        return region_with_hole

    @classmethod
    def concate_regions(cls, *regs):
        """Объединяет заданные регионы.

        Находит самую верхнюю левую и нижнюю правую
        """
        us = set()
        vs = set()
        region_type = regs[0][2]
        for region in regs:
            us.add(region[0].U)
            vs.add(region[0].V)
            us.add(region[1].U)
            vs.add(region[1].V)
        uv_max = UV(max(us), max(vs))
        uv_min = UV(min(us), min(vs))
        return (uv_min, uv_max, region_type)

    @classmethod
    def region_find_near(cls, region, regions):
        """Ищет соседствующие регионы с таким же типом"""
        region_points = [region[0]]
        region_points += [UV(region[1].U, region[0].V)]
        region_points += [UV(region[0].U, region[1].V)]
        region_points += [region[1]]
        near_regions = list()
        for cur_region in regions:
            if region[2] == cur_region[2]:
                cur_region_points = [cur_region[0]]
                cur_region_points += [UV(cur_region[1].U, cur_region[0].V)]
                cur_region_points += [UV(cur_region[0].U, cur_region[1].V)]
                cur_region_points += [cur_region[1]]
                are_near = 0
                for region_point in region_points:
                    for cur_region_point in cur_region_points:
                        if cur_region_point.IsAlmostEqualTo(region_point):
                            are_near += 1
                if are_near >= 2 and are_near < 4:
                    near_regions.append(cur_region)
        return near_regions

    @classmethod
    def region_in_same_direction(cls, region, regions, direction=0):
        """Находит регионы соответствующего направления."""
        regions_same_direction = list()
        for cur_region in regions:
            if direction == 0:
                same_direction = region[0].IsAlmostEqualTo(UV(region[0].U, cur_region[0].V)) and region[1].IsAlmostEqualTo(UV(region[1].U, cur_region[1].V))
            else:
                same_direction = region[0].IsAlmostEqualTo(UV(cur_region[0].U, region[0].V)) and region[1].IsAlmostEqualTo(UV(cur_region[1].U, region[1].V))
            if same_direction:
                regions_same_direction.append(cur_region)
        return regions_same_direction

    @classmethod
    def remove_regions(cls, region_to_remove, regions, face=None):
        new_regions = regions
        del_count = 0
        for cur_region_pos in range(0, len(regions)):
            cur_region = regions[cur_region_pos]
            for region in region_to_remove:
                if cls.regions_are_equal(cur_region, region):
                    del_count += 1
                    new_regions[cur_region_pos] = None
        if del_count > 0:
            for i in range(0, del_count):
                new_regions.remove(None)
        return new_regions

    @classmethod
    def regions_are_equal(cls, region_1, region_2):
        """Два региода одинаковы"""
        p1 = region_1[0]
        p2 = region_1[1]
        q1 = region_2[0]
        q2 = region_2[1]
        return p1.IsAlmostEqualTo(q1) and p2.IsAlmostEqualTo(q2)

    @classmethod
    def region_concate_with_near_by_direction(cls, reg, direction=0, max_length=12000, face=None, is_first=True):
        """Объединяет регионы по заданному приоритетному направлению."""
        if is_first:
            regions = copy(reg)
        else:
            regions = reg
        for region in regions:
            near_regions = cls.region_find_near(region, regions)
            near_regions = cls.region_in_same_direction(region, near_regions, direction=direction)
            if near_regions:
                new_region = cls.concate_regions(region, near_regions[0])
                temp_regions = cls.remove_regions([near_regions[0], region], regions)
                temp_regions.append(new_region)
                break
        if near_regions:
            return cls.region_concate_with_near_by_direction(temp_regions, direction=direction, max_length=max_length, face=face, is_first=False)
        else:
            return regions
