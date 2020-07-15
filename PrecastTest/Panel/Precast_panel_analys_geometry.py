# -*- coding: utf-8 -*-
from clr import StrongBox
from Autodesk.Revit.DB import BoundingBoxIntersectsFilter, FilteredElementCollector, Outline, FamilyInstance
from Autodesk.Revit.DB import BooleanOperationsUtils, BooleanOperationsType, SetComparisonResult, IntersectionResultArray, BoundingBoxIsInsideFilter
from Autodesk.Revit.DB import Line, SolidCurveIntersectionOptions, XYZ, CurveLoop, BuiltInCategory, SketchPlane, Plane
from ..Common.Precast_solid import Precast_solid
from common_scripts.line_print import Line_printer
from common_scripts import echo


class Precast_panel_analys_geometry(object):
    def make_analys_geometry(self):
        """
        Анализ геометрии для определения json.
        """
        x_plan = self.vect_ordinat
        y_plan = self.vect_abscis
        x_profile = self.vect_abscis
        y_profile = self.vect_applicat
        plan = self.find_section(
            self.center_point, direction=self.vect_applicat,  x=x_plan, y=y_plan)
        if plan:
            profile = self.find_section(
                self.center_point, direction=self.vect_ordinat, x=x_profile, y=y_profile)
            if profile:
                self.plan, self.profile, self.ut_point = self.prepare_points(
                    plan, profile, x_plan=x_plan, y_plan=y_plan, x_profile=x_profile, y_profile=y_profile)
                if self.plan and self.profile:
                    self.is_analysed = True

    def find_section(self, point=None, direction=None, x=None, y=None):
        solids = self.concate_all_elements_by_materials()
        if not solids:
            echo("У панели {} не найден ни один материал. \nВозможно не назначен параметр BDS_LayerNumber у материалов.\n".format(self))
        all_faces = {}
        # Находим поверхности, которые находятся на пересечении
        for key, solid in solids.items():
            # echo(key)
            if not key:
                continue
            face = solid.get_face_in_point(origin=point, normal=direction)
            if face:
                all_faces[key] = face
        # # преобразовываем поверхности в линии
        lines_dict = {}
        for key, faces in all_faces.items():
            lines_dict.setdefault(key, [])
            for face in faces:
                # if key == 2:
                #     self.print_face(face)
                for eloop in face.EdgeLoops:
                    for line in eloop:
                        line = line.AsCurve()
                        line = self.project_line_on_plane(
                            line, origin=point, normal=direction)
                        if line:
                            lines_dict[key].append(line)

        # # # Оставить линии, только соответствующие x и y
        points = {}
        # echo(points)
        for key, lines in lines_dict.items():
            lines = self.only_ortogonal_lines(lines, x, y)

            cur_points = self.find_intersect(lines)
            self.remove_unuse_points(cur_points, solids[key], direction, x, y)
            # if key == 2:
            #     for point in cur_points:
            #         Line_printer.print_arc(point, radius=0.02)
            # echo(key)
            # echo(cur_points)
            result = []
            if cur_points:
                self.clockwise(cur_points, result, x=x, y=y)
            else:
                raise Exception("При анализе сечения были отброшены все точки")
            points[key] = result
        return points

    def concate_all_elements_by_materials(self):
        "Объединяем все элементы панели по материалу."
        union_solids = {}
        for solid in self.solids:
            if solid.layer_number:
                union_solids.setdefault(solid.layer_number, [])
                union_solids[solid.layer_number].append(solid)
        for key, solids in union_solids.items():
            un_sol = None
            for solid in solids:
                if un_sol is None:
                    un_sol = solid.element
                else:
                    un_sol = BooleanOperationsUtils.ExecuteBooleanOperation(
                        un_sol, solid.element, BooleanOperationsType.Union)
            union_solids[key] = Precast_solid(un_sol, self.doc)
        return union_solids

    def only_ortogonal_lines(self, lines, *arg):
        "Оставляет только линии соответствующие векторам."
        res_lines = []
        for i in lines:
            for v in arg:
                check = i.Direction.IsAlmostEqualTo(
                    v) or i.Direction.IsAlmostEqualTo(v.Negate())
                if check:
                    res_lines.append(i)
        return res_lines

    def find_intersect(self, lines):
        """
        Находим пересечения в прямых.

        Принимаем линии, солид и вектор.
        делаем линии неограниченные, находим между ними пересечения.
        Если пересечения есть - заносим их в points
        После чего удаляем промежуточные точки и оставляем только крайние
        Остается пройти по часовой стрелке.
        """
        [i.MakeUnbound() for i in lines]
        points = []
        for i in lines:
            for j in lines:
                res_arr = StrongBox[IntersectionResultArray]()
                res = i.Intersect(j, res_arr)
                if res == SetComparisonResult.Equal or res == SetComparisonResult.Disjoint:
                    continue
                for k in res_arr.Value:
                    not_in_list = True
                    for point in points:
                        if point.IsAlmostEqualTo(k.XYZPoint):
                            not_in_list = False
                            break
                    if not_in_list:
                        points.append(k.XYZPoint)
        return points

    def remove_unuse_points(self, points, solid, vect, x, y, sec=False, wictory=False, step=0):
        """
        Удаляем не нужные точки.

        Удаляем точки, которые не имеют соседей(висит в воздухе)
        Удаляем промежуточные точки(3 соседа)
        Удаляем точки в одну линию, у которых 2 соседа
        Удаляем точки, у которых один сосед
        """
        next_iter = False
        point_to_removes = []
        pos = 0
        for i in points:
            neiber_left = False
            neiber_right = False
            neiber_top = False
            neiber_bottom = False
            for j in points:
                if wictory or self.point_intersect_solid((i + j) / 2, solid, vect):
                    v = (i - j).Normalize()
                    if v.IsAlmostEqualTo(x):
                        neiber_top = True
                    elif v.Negate().IsAlmostEqualTo(x):
                        neiber_bottom = True
                    elif v.IsAlmostEqualTo(y):
                        neiber_left = True
                    elif v.Negate().IsAlmostEqualTo(y):
                        neiber_right = True
            neiber_summ = neiber_left + neiber_right + neiber_top + neiber_bottom
            on_one_line = (neiber_left and neiber_right) or (
                neiber_top and neiber_bottom)
            rr = (neiber_summ == 0) or\
                (neiber_summ == 1 and sec) or\
                (neiber_summ == 2 and on_one_line) or\
                neiber_summ == 3
            if rr:
                point_to_removes.append(i)
                next_iter = True
        if next_iter:
            for i in point_to_removes:
                points.remove(i)
            self.remove_unuse_points(points, solid, vect, x, y, sec=True, step=step+1)
        elif not wictory:
            self.remove_unuse_points(
                points, solid, vect, x, y, sec=True, wictory=True, step=step+1)

    def clockwise(self, points, res=None, x=None, y=None):
        "Обходим по часовой стрелке."
        if points:
            if not res:
                min_point = self.minimum_point(points, y, x)
                res.append(min_point)
                points.remove(min_point)
                self.clockwise(points, res=res, x=y, y=x)
            else:
                point = res[-1]
                y, x = x, y
                min_point = None
                distance = float("inf")
                for p in points:
                    if x.IsAlmostEqualTo((p - point).Normalize()):
                        cur_distance = point.DistanceTo(p)
                        if cur_distance < distance:
                            min_point = p
                            distance = cur_distance
                if min_point:
                    points.remove(min_point)
                    res.append(min_point)
                    self.clockwise(points, res=res, x=x, y=y)
                else:
                    x = x.Negate()
                    for p in points:
                        if x.IsAlmostEqualTo((p - point).Normalize()):
                            cur_distance = point.DistanceTo(p)
                            if cur_distance < distance:
                                min_point = p
                                distance = cur_distance
                    if min_point:
                        points.remove(min_point)
                        res.append(min_point)
                        self.clockwise(points, res=res, x=x, y=y)

    def minimum_point(self, points, vect_1, vect_2):
        min_point = None
        min_x = float("inf")
        min_y = float("inf")
        for i in points:
            x = round(self.vector_projection(i, vect_1), 5)
            y = round(self.vector_projection(i, vect_2), 5)
            if x <= min_x:
                if y <= min_y:
                    min_point = i
                    min_x = x
                    min_y = y
        return min_point

    def vector_projection(self, point, vector):
        "Проекция вектора."
        vector = vector.Normalize()
        skalar = point.DotProduct(vector)
        return skalar

    def ultimate_minimum(self, points):
        min_x = float("inf")
        min_y = float("inf")
        min_z = float("inf")
        for i in points:
            if i.X < min_x:
                min_x = i.X
            if i.Y < min_y:
                min_y = i.Y
            if i.Z < min_z:
                min_z = i.Z
        return XYZ(min_x, min_y, min_z)

    def create_curveloop(self, points):
        cl = CurveLoop.Create([])
        prev_point = None
        for point in points:
            if prev_point is None:
                cl.Append(Line.CreateBound(points[-1], points[0]))
            else:
                cl.Append(Line.CreateBound(prev_point, point))
            prev_point = point
        return cl

    def round_xyz(self, point):
        "Возвращает координаты округленные до точности ревит."
        x, y, z = point.X, point.Y, point.Z
        return (round(x, 8), round(y, 8), round(z, 8))

    def point_intersect_solid(self, point, solid, vect):
        "Проверяет пересекает ли точка по заданному вектору солид."
        # point = self.transform.OfPoint(point)
        line = Line.CreateBound(
            point + vect * self.height/3, point - vect * self.height/3)
        res = solid.element.IntersectWithCurve(
            line, SolidCurveIntersectionOptions())
        return res.SegmentCount

    def create_curveloop(self, points):
        cl = CurveLoop.Create([])
        prev_point = None
        for point in points:
            if prev_point is None:
                cl.Append(Line.CreateBound(points[-1], points[0]))
            else:
                cl.Append(Line.CreateBound(prev_point, point))
            prev_point = point
        return cl

    def round_xyz(self, point):
        "Возвращает координаты округленные до точности ревит."
        x, y, z = point.X, point.Y, point.Z
        return (round(x, 8), round(y, 8), round(z, 8))

    def prepare_points(self, plan, profile, x_plan, y_plan, x_profile, y_profile):
        plan, ut_1 = self.prepare_point(plan, x_plan, y_plan)
        profile, ut_2 = self.prepare_point(profile, x_profile, y_profile)
        ut_point = XYZ(ut_1.X, ut_1.Y, ut_2.Z)
        return plan, profile, ut_point

    def prepare_point(self, plan, vect_1, vect_2):
        minimum_points = {}
        plan = {key: [self.transform.Inverse.OfPoint(
            i) for i in points] for key, points in plan.items()}
        for key, points in plan.items():
            minimum_points[key] = points[0]
        all_points = []
        ultimate_minimum = self.ultimate_minimum(minimum_points.values())
        layer_points = {key: i - ultimate_minimum for key,
                        i in minimum_points.items()}

        plan = {key: {"points": [point - ultimate_minimum - layer_points[key]
                                 for point in points], "point": layer_points[key]} for key, points in plan.items()}
        return plan, ultimate_minimum
    ############ Выше все, что необходимо для анализа точек #########################

    # def print_face(self, face):
    #     "Посмотреть какая плоскость нам нужна."
    #     plane = face.GetSurface()
    #     sketchPlane = SketchPlane.Create(self.doc, plane)
    #     for j in face.GetEdgesAsCurveLoops():
    #         for i in j:
    #             self.doc.Create.NewModelCurve(i, sketchPlane)

    # def print_line(self, line):
    #     p1 = line.GetEndPoint(0)
    #     p2 = line.GetEndPoint(1)
    #     p3 = p1.CrossProduct(p2)
    #     plane = Plane.CreateByThreePoints(p1, p2, p3)
    #     sketchPlane = SketchPlane.Create(self.doc, plane)
    #     self.doc.Create.NewModelCurve(line, sketchPlane)
