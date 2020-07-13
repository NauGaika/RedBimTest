import re

from Autodesk.Revit.DB import BuiltInCategory, BuiltInParameter, Transaction,\
    FilteredElementCollector, ElementId, RevitLinkInstance, FamilyInstance,\
    ElementMulticategoryFilter, ElementCategoryFilter, Options, ViewDetailLevel,\
    Solid, ElementIntersectsSolidFilter, GeometryInstance, PartUtils, BooleanOperationsUtils,\
    BooleanOperationsType, BoundingBoxIntersectsFilter, Outline, ElementIntersectsElementFilter
from math import pi, ceil
from System.Collections.Generic import List

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document


class Captures(object):
    opt_1 = Options()
    opt_1.DetailLevel = ViewDetailLevel.Medium
    opt_1.IncludeNonVisibleObjects = True
    opt_2 = Options()
    opt_2.DetailLevel = ViewDetailLevel.Medium
    rebar_found_host = List[ElementId]()

    def __init__(self, doc, parent=None, transforms=None, uidoc=None):
        """
        Начало параметризации.
        Параметрами передаются 
        doc
        1. Получить арматуру в текущем файле.
        2. Распределить арматуру по типам:
            - Системная
            - IFC
        3. Получить все хосты формообразующие текущего докоумента
        4. Найти родителей арматуры
        . Найти либ документы
        . По разнному обработать арматуру на поиск хоста
        {
            doc: transform
        }
        """

        self.transforms = transforms
        self.parent = parent
        self.doc = doc
        self.uidoc = uidoc
        echo("Начинаем работать с {}".format(self))
        self.rebar_system, self.rebar_ifc = self.find_all_rebar()
        echo("Получили арматурные стержни и разделили на IFC {} штук и системную {} штук".format(len(self.rebar_ifc), len(self.rebar_system)))
        self.hosts = self.get_parts_and_floor()
        echo("Получили формы части и плиты {}".format(len(self.hosts)))
        self.find_rebar_capture_system(self.rebar_system)
        self.find_rebar_capture_ifc(self.rebar_ifc)
        echo("Отработал поиск хостов")
        # self.lib_documents = self.get_instance_document()
        # self.parametrizetion_lib()

    def __repr__(self):
        if self.doc:
            return self.doc.Title
        return str(self.doc)

    def get_instance_document(self):
        """
        Находим все экзмепляры связей.

        Запихиваем в documents с их трансформатцией
        Сколько трансформаций. Столько и либов.
        """
        documents = {}
        els = FilteredElementCollector(self.doc).\
            OfClass(RevitLinkInstance).ToElements()
        for i in els:
            l_doc = i.GetLinkDocument()
            trans = i.GetTotalTransform()
            if l_doc not in documents.keys():
                documents[l_doc] = set()
            documents[l_doc].add(trans)
        return documents

    def parametrizetion_lib(self):
        for key, i in self.lib_documents.items():
            if key:
                self.__class__(key, parent=self, transforms=i)

    def find_all_rebar(self):
        """
        Поиск арматуры.

        Ищем всю арматуру и разделяем ее
        на IFC и
        Системную
        """
        system_rebar = set()
        ifc_rebar = set()
        rebars = FilteredElementCollector(self.doc).\
            OfCategory(BuiltInCategory.OST_Rebar).\
            WhereElementIsNotElementType().ToElements()
        for i in rebars:
            pog_met = i.LookupParameter("Рзм.ПогМетрыВкл") if i.LookupParameter("Рзм.ПогМетрыВкл") else self.doc.GetElement(i.GetTypeId()).LookupParameter("Рзм.ПогМетрыВкл")
            if pog_met and not pog_met.AsInteger():
                if isinstance(i, FamilyInstance):
                    ifc_rebar.add(i)
                else:
                    system_rebar.add(i)
        return system_rebar, ifc_rebar

    def get_parts_and_floor(self):
        """
        Получаем все возможные формообразующие в текущем документе.
        """
        els = FilteredElementCollector(self.doc).\
            WhereElementIsNotElementType().\
            OfCategory(BuiltInCategory.OST_Floors).ToElementIds()
        sel = List[ElementId]()
        res = []
        for i in els:
            parts = PartUtils.GetAssociatedParts(self.doc, i, True, True)
            fl = self.doc.GetElement(i)
            fl_par = fl.LookupParameter("Номер захватки")
            if parts.Count:
                fl_par.Set("Не учитывать")
                fl_gr = fl.LookupParameter("Орг.ГруппаВедомостьРасходаБетона").AsString()
                for j in parts:
                    pt = self.doc.GetElement(j)
                    if pt.LookupParameter("Номер захватки").AsString():
                        sel.Add(j)
                        res.append(pt)
                    pt.LookupParameter("Орг.ГруппаВедомостьРасходаБетона").Set(fl_gr)
            else:
                if fl_par.AsString() == "Не учитывать":
                    fl_par.Set("")
                if fl_par.AsString():
                    res.append(fl)
                    sel.Add(i)
        self.uidoc.Selection.SetElementIds(sel)
        return sorted(res, key=lambda x: x.LookupParameter("Номер захватки").AsString())

    def select(self, elements):
        elements = List[ElementId]([i.Id for i in elements])
        __revit__.ActiveUIDocument.Selection.SetElementIds(elements)

    def find_rebar_capture_system(self, elements):
        """
        Находим захватки системной арматуры.
        """
        # hosts = List[ElementId]([i.Id for i in self.hosts])
        elements = List[ElementId]([i.Id for i in elements])
        for host in self.hosts:
            elements_fec = FilteredElementCollector(self.doc, elements)
            bb = host.Geometry[self.opt_1].GetBoundingBox()
            filtered = BoundingBoxIntersectsFilter(Outline(bb.Min, bb.Max))
            rebars = elements_fec.WherePasses(filtered).ToElements()
            for rebar in rebars:
                host_is_found = False
                for host_solid in self.get_solids(host, opt=self.opt_2):
                    if host_is_found:
                        break
                    if isinstance(host_solid, Solid):
                        cur_line = next(iter(rebar.Geometry[self.opt_1]))
                        if host_solid.\
                                IntersectWithCurve(cur_line, None).\
                                SegmentCount:
                            rebar.LookupParameter("Номер захватки").\
                                Set(host.LookupParameter("Номер захватки").AsString())
                            host_is_found = True

    # def find_rebar_host_system(self, elements, parent=None, transforms=None):
    #     """
    #     Находим хосты системной арматуры.
    #     """

    #     rebar_without_hosts = set()
    #     for el in elements:
    #         host_is_found = False
    #         cur_line = next(iter(el.Geometry[self.opt_1]))
    #         transform_host = {}
    #         for host in self.hosts:
    #             if host_is_found:
    #                 break
    #             for host_solid in self.get_solids(host, opt=self.opt_2):
    #                 if isinstance(host_solid, Solid):
    #                     if transforms is not None:
    #                         for transform in transforms:
    #                             trans_line = cur_line.CreateTransformed(transform)
    #                             if host_solid.IntersectWithCurve(trans_line, None).SegmentCount:
    #                                 # echo("У системной арматуры {} найдена захватка в родителе {}".format(el.Id, host.Id))
    #                                 transform_host[transform] = host.Id
    #                     else:
    #                         # echo("Ищем хост")
    #                         if host_solid.IntersectWithCurve(cur_line, None).SegmentCount:
    #                             # echo("У системной арматуры {} найден захватка {}".format(el.Id, host.Id))
    #                             el.LookupParameter("Номер захватки").Set(host.LookupParameter("Номер захватки").AsString())
    #                             host_is_found = True
    #         if not host_is_found:
    #             rebar_without_hosts.add(el)
    #             echo("Для системной арматуры {} не найдена захватка".format(el.Id))
    #     if self.parent and rebar_without_hosts:
    #         echo("Ищем захватку в родителе")
    #         self.parent.find_rebar_host_system(rebar_without_hosts, transforms=self.transforms)

    def find_rebar_capture_ifc(self, elements):
        elements = List[ElementId]([i.Id for i in elements])
        for host in self.hosts:
            elements_fec = FilteredElementCollector(self.doc, elements)
            bb = host.Geometry[self.opt_1].GetBoundingBox()
            filtered = BoundingBoxIntersectsFilter(Outline(bb.Min, bb.Max))
            rebars = elements_fec.WherePasses(filtered).ToElements()
            for rebar in rebars:
                all_reb_solids = self.get_solids(rebar)
                host_is_found = False
                for rebar_solid in all_reb_solids:
                    if host_is_found:
                        break
                    for host_solid in self.get_solids(host):
                        if host_is_found:
                            break
                        try:
                            union_solid = BooleanOperationsUtils.\
                                ExecuteBooleanOperation(
                                    rebar_solid,
                                    host_solid,
                                    BooleanOperationsType.Union)
                            sum_area = rebar_solid.SurfaceArea +\
                                host_solid.SurfaceArea -\
                                union_solid.SurfaceArea
                        except:
                            sum_area = 1
                        if sum_area > 0.0001:
                            host_is_found = True
                            rebar.LookupParameter("Номер захватки").\
                                Set(host.LookupParameter("Номер захватки").\
                                    AsString())

    def find_rebar_host_ifc(self, elements):

        for el in elements:
            all_reb_solids = self.get_solids(el)
            host_is_found = False
            if all_reb_solids:
                for first_solid in all_reb_solids:
                    if host_is_found:
                        break
                    for host in self.hosts:
                        if host_is_found:
                            break
                        sum_area = 0
                        for host_solid in self.get_solids(host):
                            if host_is_found:
                                break
                            union_solid = BooleanOperationsUtils.ExecuteBooleanOperation(first_solid, host_solid, BooleanOperationsType.Union)
                            sum_area += ((first_solid.SurfaceArea + host_solid.SurfaceArea) - union_solid.SurfaceArea)
                            if sum_area > 0.0001:
                                host_is_found = True
                                el.LookupParameter("Номер захватки").Set(host.LookupParameter("Номер захватки").AsString())
                    if not host_is_found:
                        pass
                        echo("Для IFC арматуры {} не найден host".format(el.Id))
            else:
                # pass
                echo("Не найдено геометрии для IFC {}".format(self))

    def get_solids(self, el, opt=None):
        opt = opt if opt is not None else self.opt_1
        res = []
        for geom in el.Geometry[opt]:
            if isinstance(geom, GeometryInstance):
                res += [i for i in geom.GetInstanceGeometry() if isinstance(i, Solid) and i.Volume > 0]
            elif isinstance(geom, Solid) and geom.Volume > 0:
                res.append(geom)
        return res





with Transaction(doc, "Параметризация") as t:
    t.Start()
    Captures(doc, uidoc=uidoc)
    t.Commit()