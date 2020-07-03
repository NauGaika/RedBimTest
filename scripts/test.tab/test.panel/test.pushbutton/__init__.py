import re

from Autodesk.Revit.DB import BuiltInCategory, BuiltInParameter, Transaction,\
    FilteredElementCollector, ElementId, RevitLinkInstance, FamilyInstance,\
    ElementMulticategoryFilter, ElementCategoryFilter, Options, ViewDetailLevel,\
    Solid, ElementIntersectsSolidFilter, GeometryInstance
from math import pi, ceil
from System.Collections.Generic import List

doc = __revit__.ActiveUIDocument.Document


class Captures(object):
    opt_1 = Options()
    opt_1.DetailLevel = ViewDetailLevel.Medium
    opt_1.IncludeNonVisibleObjects = True
    opt_2 = Options()
    opt_2.DetailLevel = ViewDetailLevel.Medium

    def __init__(self, doc, parent=None, transforms=None):
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
        echo("Начинаем работать с {}".format(self))
        self.rebar_system, self.rebar_ifc = self.find_all_rebar()
        echo("Получили арматурные стержни и разделили на IFC {} штук и системную {} штук".format(len(self.rebar_ifc), len(self.rebar_system)))
        self.hosts = self.get_capture_forms()
        echo("Получили формы для арматуры в  количестве {}".format(len(self.hosts)))
        self.find_rebar_host_system(self.rebar_system)
        self.find_rebar_host_ifc(self.rebar_ifc)
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
            if isinstance(i, FamilyInstance):
                ifc_rebar.add(i)
            else:
                system_rebar.add(i)
        return system_rebar, ifc_rebar

    def get_capture_forms(self):
        """
        Получаем все возможные формообразующие в текущем документе.
        """
        els = FilteredElementCollector(self.doc).WhereElementIsNotElementType().OfCategory(BuiltInCategory.OST_Mass).ToElements()
        return sorted(els, key=lambda x: int(x.LookupParameter("Захватка").AsString()))

    def select(self, elements):
        elements = List[ElementId]([i.Id for i in elements])
        __revit__.ActiveUIDocument.Selection.SetElementIds(elements)

    def find_rebar_host_system(self, elements, parent=None, transforms=None):
        """
        Находим хосты системной арматуры.
        """
        rebar_without_hosts = set()
        for el in elements:
            host_is_found = False
            cur_line = next(iter(el.Geometry[self.opt_1]))
            transform_host = {}
            for host in self.hosts:
                if host_is_found:
                    break
                for host_solid in self.get_solids(host, opt=self.opt_2):
                    if isinstance(host_solid, Solid):
                        if transforms is not None:
                            for transform in transforms:
                                trans_line = cur_line.CreateTransformed(transform)
                                if host_solid.IntersectWithCurve(trans_line, None).SegmentCount:
                                    # echo("У системной арматуры {} найдена захватка в родителе {}".format(el.Id, host.Id))
                                    transform_host[transform] = host.Id
                        else:
                            # echo("Ищем хост")
                            if host_solid.IntersectWithCurve(cur_line, None).SegmentCount:
                                # echo("У системной арматуры {} найдена захватка {}".format(el.Id, host.Id))
                                el.LookupParameter("Захватка").Set(host.LookupParameter("Захватка").AsString())
                                host_is_found = True
            if not host_is_found:
                rebar_without_hosts.add(el)
                echo("Для системной арматуры {} не найдена захватка".format(el.Id))
        if self.parent and rebar_without_hosts:
            echo("Ищем захватку в родителе")
            self.parent.find_rebar_host_system(rebar_without_hosts, transforms=self.transforms)

    def find_rebar_host_ifc(self, elements):

        for el in elements:
            all_reb_solids = self.get_solids(el)
            host_is_found = False
            if all_reb_solids:
                first_solid = next(iter(all_reb_solids))
                line = next(iter(first_solid.Edges)).AsCurve()
                for host in self.hosts:
                    if host_is_found:
                        break
                    for host_solid in self.get_solids(host):
                        if isinstance(host_solid, Solid):
                            if host_solid.IntersectWithCurve(line, None).SegmentCount:
                                # echo("У IFC арматуры {} найден хост {}".format(el.Id, host.Id))
                                el.LookupParameter("Захватка").Set(host.LookupParameter("Захватка").AsString())
                                host_is_found = True
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
    Captures(doc)
    t.Commit()