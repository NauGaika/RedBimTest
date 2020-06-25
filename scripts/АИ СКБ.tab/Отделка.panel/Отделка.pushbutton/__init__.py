# coding: utf8
"""Добавляем необходимые фильтры для КЖ"""
# import os
import re
import sys
import clr
from clr import StrongBox

from Autodesk.Revit.UI import ExternalEvent, IExternalEventHandler
from Autodesk.Revit.DB.Architecture import Room
from Autodesk.Revit.DB import FilteredElementCollector, Options, BooleanOperationsUtils, BooleanOperationsType, FaceIntersectionFaceResult, Plane, SketchPlane, Transaction, \
CurveArray, XYZ, UV, IntersectionResultArray, Line, GraphicsStyle, PlanarFace, SetComparisonResult, SolidCurveIntersectionOptions, SolidCurveIntersectionMode
from common_scripts.get_elems.Get_revit_elements import Get_revit_elements as RB_FilteredElementCollector
from Autodesk.Revit.DB import BuiltInCategory, Transaction, ViewSheet, FilteredElementCollector, Wall, BuiltInParameter, View, ViewSchedule
from Autodesk.Revit.UI import ExternalEvent, IExternalEventHandler
# from System.Collections.Generic import List


uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
curview = uidoc.ActiveGraphicalView
selection = [doc.GetElement(elId) for elId in __revit__.ActiveUIDocument.Selection.GetElementIds()]


class Line_by_room(IExternalEventHandler):
    """Линии в комнате по примыкающим стенам
    
    """
    __all_walls = {}
    __wall_levels = {}
    view_option = Options()
    intersect_option_inside = SolidCurveIntersectionOptions()
    intersect_option_outside = SolidCurveIntersectionOptions()
    intersect_option_outside.ResultType = SolidCurveIntersectionMode.CurveSegmentsOutside
    __graphic_syles = {}
    offset_length = to_feet(100)
    tollerance = to_feet(25)
    
    @property
    def graphic_syles(self):
        """Графические стили проекта
        
        """
        if not self.__graphic_syles:
            els = FilteredElementCollector(doc).OfClass(GraphicsStyle).ToElements()
            els = {el.Name: el for el in els}
            self.__graphic_syles = els
        return self.__graphic_syles

    @property    
    def walls(self):
        """Получаем стены
        
        Сейчас берем все стены в проекте. Нужно бы придумать
        как брать стены которые рядышком.
      """
        if not self.__all_walls:
            walls = {}
            for i in FilteredElementCollector(doc, curview.Id).OfClass(Wall).ToElements():
                walls.setdefault(i.Name, set())
                walls[i.Name].add(i)
            self.__all_walls = walls
        return self.__all_walls
        
    @property
    def wall_levels(self):
        """Уровни стен
        
        Считаем уровень стен через поиск центра тела
        После этого берем оттуда координату Z.
        
      """
        if not self.__wall_levels:
            for i in self.walls.keys():
                self.__wall_levels.setdefault(i, 0)
                e = next(iter(self.walls[i]))
                e = next(e.Geometry[self.view_option].GetEnumerator()).ComputeCentroid().Z
                self.__wall_levels[i] = e
        return self.__wall_levels
    

    def __init__(self, rooms):
        """Начинаем работу
        
      """
        self.room_lines = []
        for room in rooms:
            if isinstance(room, Room):
                self.room_faces = self.get_element_faces(room)
                intersect_walls = self.get_intersect_wall(room)
                intersect_walls = {i: k for i,k in intersect_walls.items() if k}
                offset = 0
                for type_name, lines in intersect_walls.items():
                    offset += 1
                    lines = self.line_trimming(lines)
                    lines = self.create_rings(lines)
                    lines = self.add_offset(lines, offset)
                self.room_lines.append(intersect_walls)
        wall_names = set()
        for room in self.room_lines:
            for i in room.keys():
                wall_names.add(i)
        FORM.Start(len(wall_names) + 2)
        pp = 1
        self.form_val = {}
        for k in wall_names:
            cur = FORM.GetLines(pp).add_textbox(k, '')
            cur.Height = 24
            FORM.GetLines(pp).add_label("Смещение для {}".format(k))
            self.form_val.setdefault(k, cur)
            pp += 1
        
        but_create = FORM.GetLines(pp).add_button('Выполнить')
        but_cancel = FORM.GetLines(pp+1).add_button('Отмена')
        
        exEvent = ExternalEvent.Create(self)
        
        but_cancel.AddFunction(FORM.Close)
        but_create.AddFunction(self.start)
        
        FORM.calculate_size()
        FORM.Create(exEvent)

    def start(self):
        FORM.exEvent.Raise()
        
    def Execute(self, app):
        try:
            self.form_val = {i: to_feet(int(self.form_val[i].GetValue())) for i in self.form_val.keys() if self.form_val[i].GetValue().isdigit()}
            with Transaction(doc, 'Рисуем линии') as t:
                t.Start()
                for room in self.room_lines:
                    # echo(room)
                    for type_name, lines in room.items():
                        if type_name in self.form_val.keys():
                            lines = self.add_offset(lines, self.form_val[type_name])
                            # echo(self.get_graphic_styles(type_name))
                            self.print_line_by_face(lines, self.get_graphic_styles(type_name), type_name)
                        else:
                            message('Не задан отступ для типоразмера {} линия создана не будте'.format(type_name))
                t.Commit()
        except:
            echo(sys.exc_info()[1])
        FORM.Close()
        
    def GetName(self):
        return 'Рисуем линии отделки'
        
    def line_trimming(self, lines):
        """Обрезка линий, которые выступают друг за друга
        
         формируем линии путем попытки пересечения их.
         Если линии пересекается с другими два раза
         два пересечения и есть точки этой линии
         
         если линия пересекается один раз. То ближняя точка заменяется 
         той, которая пересеклась
         
         если линия не пересекается - оставляем без изменений
        
        """
        new_lines = []
        for line_1 in lines:
            new_points = list()
            p1 = line_1.GetEndPoint(0)
            p2 = line_1.GetEndPoint(1)
            for line_2 in lines:
                intersect_result = StrongBox[IntersectionResultArray]()
                intersect_result_text = line_1.Intersect(line_2, intersect_result)
                intersect_result = intersect_result.Value
                if intersect_result_text == SetComparisonResult.Overlap and intersect_result:
                    for i in intersect_result: new_points.append(i.XYZPoint)
            if len(new_points) == 2:
                new_lines.append(Line.CreateBound(new_points[0], new_points[1]))
            elif len(new_points) == 1: 
                if p1.DistanceTo(new_points[0]) > p2.DistanceTo(new_points[0]):
                    new_lines.append(Line.CreateBound(p1, new_points[0]))
                else:
                    new_lines.append(Line.CreateBound(p2, new_points[0]))
            else:
                new_lines.append(line_1)
        return new_lines
                
    def add_offset(self, lines, offset):
        """Добавляем отступ линии
        
        """
        new_lines = []
        for line in lines:
            points = [line.GetEndPoint(0), line.GetEndPoint(1)]
            for point_pos in range(0,2):
                point = points[point_pos]
                faces = set()
                for face in self.room_faces:
                    plane = face.GetSurface()
                    project_point = plane.Project(point)
                    # echo(project_point)
                    if project_point:
                        if project_point[1] < self.tollerance:
                            faces.add(face)
                normal_sum = XYZ(0,0,0)
                for face in faces:
                    normal_sum += face.ComputeNormal(UV())
                if abs(normal_sum.X) > 0.0001: dev_x = abs(normal_sum.X)
                else: dev_x = 1
                if abs(normal_sum.Y) > 0.0001: dev_y = abs(normal_sum.Y)
                else: dev_y = 1

                normal_sum = XYZ(normal_sum.X / dev_x, normal_sum.Y / dev_y, 0)
                point -= normal_sum * offset
                points[point_pos] = point
            new_lines.append(Line.CreateBound(points[0], points[1]))
        return new_lines
    
    def have_pair(self, point, lines):
        count = 0
        for line in lines:
            p1 = line.GetEndPoint(0)
            p1 = line.GetEndPoint(1)
            
    def get_element_faces(self, elem):
        geom = elem.Geometry[self.view_option]
        faces = []
        for i in geom:
            faces += list(i.Faces)
        return faces
        
    def get_graphic_styles(self, type_name):
        """Получаем графический стиль
        
        исходя из имени типоразмера стены
        
        """
        for i in self.graphic_syles.keys():
            if i in type_name and i != '0':
                return self.graphic_syles[i]
                
    def get_intersect_wall(self, room):
        """Получаем конаты и находим все стены которые с ними пересекаются
        
            потом получаем общие грани. get_common_edges возвращает линии
            
            если общие линии найдены - объединяем их рекурсивно.
            необходимо создавать изначально массив good_lines т.к. concate_lines
            ничего не возвращает.
            
            в good_lines запишутся все линии, которые нам необходимы
            
            добавляем в словарь walls все линии с ключем = типоразмеру стены.
            
        """
        walls = {}
        for wall_name, cur_walls in self.walls.items():
            wall_solids, room_solid = self.get_wall_intersect(room, cur_walls)
            lines = self.get_common_edges(room_solid, wall_solids)
            if lines:
                good_lines = []
                self.concate_lines(lines, good_lines=good_lines)
                lines = good_lines
            walls.setdefault(wall_name, lines)
        return walls

    def concate_lines(self, lines, good_lines=None, depth=0):
        """Объеденяет линии рекрсивно. 
        
        в good_line Необходимо передавать массив.
        В него как раз будет записываться уже объедененные линии
        Как вариант найти как вернуть good_lines. Пока что не заморачивался
        
        """      
        if lines:
            line = lines.pop()
            
            new_line = None
            
            p1 = line.GetEndPoint(0)
            p2 = line.GetEndPoint(1)
            
            unbound_line = line.Clone()
            unbound_line.MakeUnbound()
            
            chean = []
            
            for cur_line in lines:
                intersection_result_type = unbound_line.Intersect(cur_line)
                if intersection_result_type == SetComparisonResult.Superset and self.common_end_points(cur_line, line):
                    chean.append(cur_line)
            if chean:
                for i in chean:
                    lines.remove(i)
                    new_line = self.create_longest_lines(chean + [line])
                lines.append(new_line)
            else:
                good_lines.append(line)
            self.concate_lines(lines, good_lines=good_lines, depth=depth)

    def common_end_points(self, line_1, line_2):
        """Проверяем совпадает ли какой-нибудь конец у двух линий.
        
        """
        cp1 = line_1.GetEndPoint(0)
        cp2 = line_1.GetEndPoint(1)
        p1 = line_2.GetEndPoint(0)
        p2 = line_2.GetEndPoint(1)
        if cp1.DistanceTo(p1) < self.tollerance  or cp1.DistanceTo(p2) < self.tollerance or cp2.DistanceTo(p1) < self.tollerance or cp2.DistanceTo(p2) < self.tollerance:
            return True
        else:
            cp1_to_line_2 = line_1.Project(p1)
            cp2_to_line_2 = line_1.Project(p2)
            p1_to_line_1 = line_2.Project(p1)
            p2_to_line_1 = line_2.Project(p2)
            if ((cp1_to_line_2 and cp1_to_line_2.Distance < self.tollerance) and (cp2_to_line_2 and cp2_to_line_2.Distance < self.tollerance)) or ((p1_to_line_1 and p1_to_line_1.Distance < self.tollerance) and (p2_to_line_1 and p2_to_line_1.Distance < self.tollerance)):
                return True

    def get_new_line(self, line_1, line_2):
        
        cp1 = line_1.GetEndPoint(0)
        cp2 = line_1.GetEndPoint(1)
        p1 = line_2.GetEndPoint(0)
        p2 = line_2.GetEndPoint(1)
        
        line_1_unbound = line_1.Clone()
        line_1_unbound.MakeUnbound()
        line_2_unbound = line_2.Clone()
        line_2_unbound.MakeUnbound()
        
        inter_res = StrongBox[IntersectionResultArray]()
        inter_res_text = line_1_unbound.Intersect(line_2_unbound, inter_res)
        if inter_res_text == SetComparisonResult.Overlap:
            inter_point = next(iter(inter_res)).XYZPoint
            if cp1.DistanceTo(inter_point) < self.tollerance and cp2.DistanceTo(inter_point) > self.tollerance:
                return Line.CreateBound(cp2, inter_point)
            elif cp2.DistanceTo(inter_point) < self.tollerance and cp1.DistanceTo(inter_point) > self.tollerance:
                return Line.CreateBound(cp1, inter_point)
        
    def create_longest_lines(self, lines):
        """Делаем из поданных линий максимально длинную.
        
        """
        all_points = self.all_lines_points(lines)
        p1, p2 = self.max_distance(all_points)
        return Line.CreateBound(p1, p2)

    def max_distance(self, points):
        """Из массива точек возвращаем две точки, которые находятся  на максимальном расстоянии."""
        max_distance = (0, 0, 0)
        args = []
        for i in points:
            for b in points:
                distance = i.DistanceTo(b)
                if distance > max_distance[2]:
                    max_distance = (i, b, distance)
        return (max_distance[0], max_distance[1])

    def print_line_by_face(self, lines, graphic_syles, name):
        """Рисует линии для которых есть типоразмер
        
        На вход подаем:
        lines - массив линий
        graphic_syles - элемент графического стиля
        name - имя типоразмера стены
        
        """
        if lines:
            line_set = set()
            test = CurveArray()
            if not graphic_syles:
                message("Не найден стиль для типоразмера {}".format(name))
                return
            for i in lines:
                # if i.ApproximateLength > self.tollerance:
                test.Append(i)
            res = doc.Create.NewDetailCurveArray(curview, test)
            for i in res:
                i.LineStyle = graphic_syles

    def get_common_edges(self, room_solid, solids):
        """Получает общие грани у солидов.
        
        Логика получения:
            находим геометрический центр каждого солида из solids
            проходим по всем поверхностям данного солида
            проецируем на Face этот центр масс
            проверяем лежит ли данная точка на какой-либо из поверхностей
                room_solid. Если лижит - добавляем поверхность в faces
            проходим по всем выбранным поверхностям, по ее граням
                если линия не вертикальна - добавляем ее в lines - set()
                
            приводим все линии к горизонтальной Z - которых соответствует origin
                текущего вида
            убираем все null из массива
            возвращаем массив линий.
        
        """
        lines = set()
        faces = set()
        for solid in solids:
            wall_cenroid = solid.ComputeCentroid()
            for face in solid.Faces:
                if isinstance(face, PlanarFace):
                    for general_face in room_solid.Faces:
                        centroid_project = face.Project(wall_cenroid)
                        if centroid_project:
                            center = centroid_project.XYZPoint
                            result = general_face.Project(center)
                            if result and result.Distance < 0.00001:
                                # echo(face)
                                faces.add(face)
        for face in faces:
            for edge_loop in face.EdgeLoops:
                for line in edge_loop:
                    line = line.AsCurve()
                    if self.is_not_vertical(line):
                        intersection_result_inside = room_solid.IntersectWithCurve(line, self.intersect_option_inside)
                        intersection_result_outside = room_solid.IntersectWithCurve(line, self.intersect_option_outside)
                        if intersection_result_inside.SegmentCount > 0:
                            max_distance_outside = 0
                            if intersection_result_outside.SegmentCount:
                                max_distance_outside = intersection_result_outside.GetCurveSegment(0).ApproximateLength
                                # if max_distance_outside > 1:
                                    # self.print_line(intersection_result_inside.GetCurveSegment(0))
                            for i in range(0, intersection_result_inside.SegmentCount):
                                inter_line = intersection_result_inside.GetCurveSegment(i)
                                if inter_line.ApproximateLength > max_distance_outside + 0.0001:
                                    lines.add(inter_line)
        lines = [self.line_z_to_curview(line) for line in lines]
        lines = [i for i in lines if i is not None]
        return lines               
        
    def print_line(self, line):
        """Рисуем линию."""
        doc.Create.NewDetailCurve(curview, self.line_z_to_curview(line))
        
    def line_z_to_curview(self, line):
        """Обнуляет координату Z у линии."""
        z = curview.Origin.Z
        p1 = line.GetEndPoint(0)
        p2 = line.GetEndPoint(1)
        p1 = XYZ(p1.X, p1.Y, z)
        p2 = XYZ(p2.X, p2.Y, z)
        return Line.CreateBound(p1,p2)
    
    def is_not_vertical(self, line):
        """Проверяет не является ли линия вертикальной."""
        vec = (line.GetEndPoint(0) - line.GetEndPoint(1)).Normalize()
        if not (vec.IsAlmostEqualTo(XYZ(0,0,1)) or vec.IsAlmostEqualTo(XYZ(0,0,-1))):
            return True
        
    def get_wall_intersect(self, room, walls):
        """Находим стены которые пересекаются с текущим помещением"""
        room_geometries = room.Geometry[self.view_option].GetEnumerator()
        walls_intersect = []
        for room_geometry in room_geometries:
            for i in walls:
                wall_geometries = i.Geometry[self.view_option].GetEnumerator()
                for wall_geometry in wall_geometries:
                    union_solid = BooleanOperationsUtils.ExecuteBooleanOperation(room_geometry, wall_geometry, BooleanOperationsType.Union)
                    sum_area = ((room_geometry.SurfaceArea + wall_geometry.SurfaceArea) - union_solid.SurfaceArea)
                    if sum_area > 0.0001:
                        walls_intersect.append(wall_geometry)
        return (walls_intersect, room_geometry)
    
    def all_lines_points(self, lines):
        """Все точки линий
        
        """
        all_points = []
        for i in lines:
            all_points.append(i.GetEndPoint(0))
            all_points.append(i.GetEndPoint(1))
        return all_points
        
    def create_rings(self, lines):
        """Создание колец
        
        """
            # echo('является ли {} кольцом?'.format(line_name))
            # echo(self.is_ring(lines))
        new_lines = []
        for line_1 in lines:
            for line_2 in lines:
                inter_res = self.get_new_line(line_1, line_2)
                if inter_res:
                    line_1 = inter_res
            new_lines.append(line_1)
        return new_lines
                    

    def is_ring(self, lines):
        """Являются ли заданные линии кольцом
      
        У каждого кольца должно быть парное количество одинаковых точек.
        иначе это не кольцо
        """
        points = self.all_lines_points(lines)
        
        for point_1 in points:
            count = 0
            for point_2 in points:
                echo(count)
                if point_1.IsAlmostEqualTo(point_2):
                    count += 1
            # if count < 2:
                # return
        return True
handler = Line_by_room(selection)

# with Transaction(doc, 'test') as t:
    # t.Start()
    # Line_by_room(selection)
    # t.Commit()