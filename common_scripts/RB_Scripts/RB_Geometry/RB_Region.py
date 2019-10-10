# coding: utf8
"""Пакет скриптов по работе с регионами."""
import clr
from copy import copy
from common_scripts import echo
from Autodesk.Revit.DB import UV, Line, SetComparisonResult, IntersectionResultArray
from common_scripts.line_print import Line_printer


class RB_Region:
    """Класс по созданию и работе с регионами."""
    test = True
    def __init__(self, p1, p2, face, protect_length):
        self.points = (p1, p2)
        self.face = face
        self.pr = 3.28 * 30 / 1000
        self.protect_length = protect_length
        self._protect = None
        self._sibling_rerend = True
        self._siblings = {
            'top': [],
            'bottom': [],
            'left': [],
            'right': []
        }

    def to_xyz(self, points):
        """Преобразует переданные точки в XYZ."""
        res = None
        if isinstance(points, tuple) or isinstance(points, list):
            res = []
            for point in points:
                if isinstance(point, UV):
                    res.append(self.face.Evaluate(point))
            res = tuple(res)
        if isinstance(points, UV):
            res = self.face.Evaluate(points)
        return res

    @property
    def protect_corners(self):
        corner = self.to_xyz(self.corners)
        XVect = self.face.XVector
        YVect = self.face.YVector
        p1 = corner[0] + XVect * self.protect['left']
        p4 = corner[3] + XVect * self.protect['left']
        p2 = corner[1] - XVect * self.protect['right']
        p3 = corner[2] - XVect * self.protect['right']

        p1 += YVect * self.protect['top']
        p2 += YVect * self.protect['top']
        p3 -= YVect * self.protect['bottom']
        p4 -= YVect * self.protect['bottom']
        if self.siblings()['top']:
            if not self.protect['top']:
                p3 += YVect * self.pr
                p4 += YVect * self.pr
        if self.siblings()['bottom']:
            if not self.protect['bottom']:
                p1 -= YVect * self.pr
                p2 -= YVect * self.pr
        if self.siblings()['left']:
            if not self.protect['left']:
                p1 -= XVect * self.pr
                p4 -= XVect * self.pr
        if self.siblings()['right']:
            if not self.protect['right']:
                p2 += XVect * self.pr
                p3 += XVect * self.pr

        return (p1, p2, p3, p4)

    @property
    def corners(self):
        """Возвращает все 4 угла региона."""
        p1 = self.points[0]
        p2 = UV(self.points[1].U, self.points[0].V)
        p3 = self.points[1]
        p4 = UV(self.points[0].U, self.points[1].V)
        return (p1, p2, p3, p4)


    @property
    def is_hole(self):
        """Является ли регион отверстием."""
        center = (self.points[1] - self.points[0]) / 2 + self.points[0]
        return not self.face.IsInside(center)

    @property
    def protect(self):
        """Определяет нужен ли защитный слой данному региону."""
        if self._protect is None:
            self._protect = {'top': 0, 'left': 0, 'bottom': 0, 'right': 0}
            if not self.is_hole:
                all_points = self.to_xyz(self.corners)
                pos = {}
                pos['top'] = Line.CreateBound(all_points[0], all_points[1])
                pos['right'] = Line.CreateBound(all_points[1], all_points[2])
                pos['bottom'] = Line.CreateBound(all_points[3], all_points[2])
                pos['left'] = Line.CreateBound(all_points[0], all_points[3])
                for el in pos.keys():
                    done = False
                    for cl in self.face.GetEdgesAsCurveLoops():
                        if done:
                            break
                        for line in cl:
                            res = line.Intersect(pos[el])
                            if res != SetComparisonResult.Disjoint and res != SetComparisonResult.Overlap and res != SetComparisonResult.Subset:
                                self._protect[el] = self.protect_length
                                done = True
                                break
        return self._protect

    def concate_regions(self, *regs):
        """Объединяет заданные регионы.

        Находит самую верхнюю левую и нижнюю правую
        """
        us = [self.points[0].U, self.points[1].U]
        vs = [self.points[0].V, self.points[1].V]
        for region in regs:
            us.append(region.points[0].U)
            vs.append(region.points[0].V)
            us.append(region.points[1].U)
            vs.append(region.points[1].V)
            uv_max = UV(max(us), max(vs))
            uv_min = UV(min(us), min(vs))
            self.points = (uv_min, uv_max)

    def is_bordered_in_face(self, faces=None):
        """Проверяет лежит ли данный регион на поверхности."""
        for face in faces:
            distance_1 = round(face.Project(self.face.Evaluate(self.points[0])).Distance, 5)
            distance_2 = round(face.Project(self.face.Evaluate(self.points[1])).Distance, 5)
            if distance_2 == 0 or distance_1 == 0:
                return face

    def siblings(self, regions=False):
        if self._sibling_rerend and regions:
            lines = self.lines
            corners = self.to_xyz(self.corners)
            # Line_printer.print_region(self, color="Толстая синяя")
            for pos, region in enumerate(regions):
                if region != self and not region.is_hole:
                    is_sibling = 0
                    region_corners = region.to_xyz(region.corners)
                    for line in lines.values():
                        for p in region_corners:
                            res = line.Project(p)
                            if int(res.Distance*10000) == 0:
                                is_sibling += 1
                    for line in region.lines.values():
                        for p in corners:
                            res = line.Project(p)
                            if int(res.Distance*10000) == 0:
                                is_sibling += 1
                    if is_sibling > 0:
                        if region.corners[0].V > self.corners[0].V:
                            self._siblings['top'].append(region)
                        if region.corners[2].V < self.corners[2].V:
                            self._siblings['bottom'].append(region)
                        if region.corners[0].U < self.corners[0].U:
                            self._siblings['left'].append(region)
                        if region.corners[1].U > self.corners[1].U:
                            self._siblings['right'].append(region)
            self._sibling_rerend = False
            return self._siblings
        else:
            return self._siblings

    @property
    def lines(self):
        """Создает линии по граням региона"""
        p1, p2, p3, p4 = self.to_xyz(self.corners)
        elem = {
            'top': Line.CreateBound(p1, p2),
            'right': Line.CreateBound(p2, p3),
            'left': Line.CreateBound(p4, p1),
            'bottom': Line.CreateBound(p3, p4)
        }
        return elem

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.points[0].IsAlmostEqualTo(other.points[0]) and \
                self.points[1].IsAlmostEqualTo(other.points[1])

    def __str__(self):
        return str(self.points[0])  + ' -> ' + str(self.points[1]) + ' whole= ' + str(self.is_hole)

    @classmethod
    def region_bordered_face(cls, regions, faces, region_face):
        """Ищет регионы, которые одной гранью лежат на поверхности."""
        new_regions = []
        for face in faces:
            for region in regions:
                distance_1 = round(face.Project(region_face.Evaluate(region[0])).Distance, 5)
                distance_2 = round(face.Project(region_face.Evaluate(region[1])).Distance, 5)
                if distance_2 == 0 or distance_1 == 0:
                    new_regions.append(region + [face])
                else:
                    new_regions.append(region + [None])
        return new_regions

    @classmethod
    def get_all_corner(cls, region, face=None):
        """Возвращает все углы данного региона."""
        pr1, pr2 = region[0], region[1]
        p1 = pr1
        p2 = UV(pr2.U, pr1.V)
        p3 = pr2
        p4 = UV(pr1.U, pr2.V)
        if face is None:
            return (p1, p2, p3, p4)
        return (face.Evaluate(p1), face.Evaluate(p2), face.Evaluate(p3), face.Evaluate(p4))

    @property
    def center(self):
        """Возвращает все углы данного региона."""
        p1, p2, p3, p4 = self.corners

        pt1 = p2 - p1
        pt2 = p4 - p1
        return p1 + (pt2 + pt1) / 2


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
    def create_regions_by_point(cls, points, face, protect_length):
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
                    elem = cls(point, v_point, face, protect_length)
                    if elem not in region:
                        region.append(elem)
        return region

    @classmethod
    def region_concate_with_near_by_direction(
                                              cls,
                                              reg,
                                              direction=0,
                                              max_length=12000,
                                              is_first=True,
                                              iter=1):

        """Объединяет регионы по заданному приоритетному направлению."""
        if is_first:
            regions = list()
            for i in reg:
                regions.append(cls(i.points[0], i.points[1], i.face, i.protect_length))
        else:
            regions = reg

        for region in regions:
            near_regions = cls.region_find_near(region, regions)
            near_regions = cls.region_in_same_direction(region, near_regions, direction=direction)
            if near_regions:
                region.concate_regions(*near_regions)
                break
        if near_regions:
            while near_regions:
                elem = near_regions.pop()
                regions.remove(elem)
            cls.region_concate_with_near_by_direction(regions, direction=direction, max_length=max_length, is_first=False, iter=iter+1)
        return regions

    @classmethod
    def region_find_near(cls, region, regions):
        """Ищет соседствующие регионы с таким же типом."""
        near_regions = list()
        for cur_region in regions:
            if region.is_hole == cur_region.is_hole:
                are_near = 0
                for region_point in region.corners:
                    for cur_region_point in cur_region.corners:
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
                same_direction = region.points[0].IsAlmostEqualTo(UV(region.points[0].U, cur_region.points[0].V)) and region.points[1].IsAlmostEqualTo(UV(region.points[1].U, cur_region.points[1].V))
            else:
                same_direction = region.points[0].IsAlmostEqualTo(UV(cur_region.points[0].U, region.points[0].V)) and region.points[1].IsAlmostEqualTo(UV(cur_region.points[1].U, region.points[1].V))
            if same_direction:
                regions_same_direction.append(cur_region)
        return regions_same_direction
