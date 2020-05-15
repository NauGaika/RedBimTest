import re
from Autodesk.Revit.DB import FilteredElementCollector, FamilyInstance, Transaction
from Autodesk.Revit.DB import Extrusion, Sweep, Blend, ModelLine, Revolution, Sweep, SweptBlend, ModelArc
from Autodesk.Revit.DB import Dimension, ElementId, ReferencePlane, GeomCombination, CurveElement, TextElement, Control, FilledRegion, SpatialElementFromToCalculationPoints
from Autodesk.Revit.DB import Group, LinearArray, RadialArray, GroupType
from System.Collections.Generic import List

doc = __revit__.ActiveUIDocument.Document

class Family_Complex():
    extrusion_cats = [Extrusion, Sweep, Blend, Revolution, Sweep, SweptBlend]

    def __init__(self, doc, is_instance=False, analis_instance=False):
        self.is_instance = is_instance
        self.analis_instance = analis_instance
        self._json_obj = None
        self.doc = doc
        self.fm = doc.FamilyManager

        self._arrays = None
        self._groups_childs = None
        self._group_element = None

        self._copied_elements = None

        self._referance_planes = None
        self._dimensions = None
        self._lines = None
        self._geometry_combinations = None
        self._family_instances = None
        self._text_elements = None
        self._filled_regions = None

        self.controls = FilteredElementCollector(self.doc).OfClass(Control).ToElementIds()
        self.parameters = list(self.fm.GetParameters())

        self.json_obj
        self.check_profile_family()
        echo("{}: {} баллов без учета вложенных".format(self, self.summa))
        if self.analis_instance:
            self.__class__.analys_symbols(self.family_symbols, doc=self.doc, parent=self)
        if not self.is_instance:
            echo(self.json_obj)
            echo("{}: {} баллов с учетом вложенных".format(self, self.summa))

    # Работа с массивами
    @property
    def arrays(self):
        "Все массивы."
        if not self._arrays:
            self._arrays = self.get_elements_by_cats([LinearArray, RadialArray]).ToElementIds()
            self._arrays = List[ElementId](self._arrays)
            self.remove_copyes(self._arrays)
        return self._arrays

    @property
    def copied_of_array(self):
        "Группы, которые являются копиями."
        copied_array = []
        for arr in self.arrays:
            arr = self.doc.GetElement(arr)
            copied_array += list(arr.GetCopiedMemberIds())
            return copied_array

    # Работа с группами
    @property
    def group_element(self):
        "Все группы."
        if not self._group_element:
            return FilteredElementCollector(self.doc).OfClass(Group)

    @property
    def groups_childs(self):
        "Для каждой группы находим детей."
        if not self._groups_childs:
            self._groups_childs = {}
            for i in FilteredElementCollector(self.doc).OfClass(GroupType).ToElements():
                groups = list(i.Groups)
                if groups:
                    el = groups.pop()
                    self._groups_childs.setdefault(el.Id, [])
                    self._groups_childs[el.Id] += [c.Id for c in groups]
        return self._groups_childs

    @property
    def copied_elements(self):
        if not self._copied_elements:
            self._copied_elements = []
            for i in self.groups_childs.values():
                for j in i:
                    self._copied_elements += list(self.doc.GetElement(j).GetMemberIds())
        return List[ElementId](self._copied_elements)

    def remove_copyes(self, elements):
        elem_to_remove = []
        for i in elements:
            if self.copied_elements.Contains(i):
                elem_to_remove.append(i)
        for i in elem_to_remove:
            elements.Remove(i)

    @property
    def referance_planes(self):
        "Опорные плоскости."
        if self._referance_planes is None:
            self._referance_plane = List[ElementId](FilteredElementCollector(self.doc).OfClass(ReferencePlane).ToElementIds())
            self.remove_copyes(self._referance_plane)
            return self._referance_plane

    @property
    def dimensions(self):
        "Зависимости и размеры."
        if self._dimensions is None:
            self._dimensions = List[ElementId](FilteredElementCollector(self.doc).OfClass(Dimension).ToElementIds())
            self.remove_copyes(self._dimensions)
        return self._dimensions

    @property
    def lines(self):
        "Все линии."
        if self._lines is None:
            self._lines = List[ElementId](FilteredElementCollector(self.doc).OfClass(CurveElement).ToElementIds())
            self.remove_copyes(self._lines)
        return self._lines

    @property
    def room_calculate(self):
        "Все линии."
        if not hasattr(self, "_room_calculate"):
            self._room_calculate = List[ElementId](FilteredElementCollector(self.doc).OfClass(SpatialElementFromToCalculationPoints).ToElementIds())
            self.remove_copyes(self._room_calculate)
        return self._room_calculate

    @property
    def geometry_combinations(self):
        "Комбинации геометрии."
        if self._geometry_combinations is None:
            self._geometry_combinations = List[ElementId](FilteredElementCollector(self.doc).OfClass(GeomCombination).ToElementIds())
            self.remove_copyes(self._geometry_combinations)
        return self._geometry_combinations

    @property
    def geometry_combination_members(self):
        "Элеметнов в комбинациях."
        els = []
        for i in self.geometry_combinations:
            i = self.doc.GetElement(i)
            els += list([j.Id for j in i.AllMembers])
        els = List[ElementId](els)
        self.remove_copyes(els)
        return els

    @property
    def family_instances(self):
        "Экземпляры семейств."
        if self._family_instances is None:
            self._family_instances = List[ElementId](FilteredElementCollector(self.doc).OfClass(FamilyInstance).ToElementIds())
            self.remove_copyes(self._family_instances)
        return self._family_instances

    @property
    def text_element(self):
        "Текстовые элементы."
        if self._text_elements is None:
            self._text_elements = List[ElementId](FilteredElementCollector(self.doc).OfClass(TextElement).ToElementIds())
            self.remove_copyes(self._text_elements)
        return self._text_elements

    @property
    def filled_regions(self):
        "Заливки и маскировки."
        if self._filled_regions is None:
            self._filled_regions = List[ElementId](FilteredElementCollector(self.doc).OfClass(FilledRegion).ToElementIds())
            self.remove_copyes(self._filled_regions)
        return self._filled_regions

    @property
    def family_symbols(self):
        "Вложенные семейства."
        instances = FilteredElementCollector(self.doc).OfClass(FamilyInstance).ToElements()
        symbs = set()
        for i in instances:
            symbs.add(i.Symbol.Id)
        return symbs

    def __str__(self):
        return self.doc.Title

    @classmethod
    def analys_symbols(cls, symbs_ids, doc=None, parent=None):
        for s_id in symbs_ids:
            fam = doc.GetElement(s_id)
            family = doc.EditFamily(fam.Family)
            fm = cls(family, is_instance=True)
            parent.add_to_json(fm.json_obj)
            family.Close(False)

    @property
    def json_obj(self):
        if self._json_obj is None:
            self._json_obj = {
                "solids": self.geometry.Count,
                "params": round(len(self.parameters)) * 0.5,
                "referance_planes": self.referance_planes.Count,
                "lines": self.lines.Count,
                "dimenisons": round(self.dimensions.Count * 0.7),
                "geometry_combinations": self.geometry_combinations.Count,
                "geometry_combination_members": self.geometry_combination_members.Count,
                "instances": self.family_instances.Count,
                "families": len(self.family_symbols),
                "formulas": round(self.formulas_len * 0.5),
                "text_elements": self.text_element.Count,
                "controls": self.controls.Count,
                "filled_regions": self.filled_regions.Count,
                "arrays": self.arrays.Count,
                "groups": len(self.groups_childs.keys()),
                "room_calculate": self.room_calculate.Count,
            }
        return self._json_obj

    @property
    def summa(self):
        res = 0
        for i in self.json_obj.values():
            res += i
        return res

    def show_info(self):
        echo("Количество опорных плоскостей = {}".format(self.referance_planes.Count))
        echo("Количество зависимостей = {}".format(self.dimensions.Count))
        echo("Количество параметров = {}".format(len(self.parameters)))
        echo("Количество модельных линий = {}".format(self.lines.Count))
        echo("Количество комбинаций геометрии = {}".format(self.geometry_combinations.Count))
        echo("Количество элементов в комбинации = {}".format(self.geometry_combination_members.Count))
        echo("Количество вложенных семейств = {}".format(len(self.family_symbols)))
        echo("Количество экземпляров семейств = {}".format(self.family_instances.Count))
        echo("Количество операций в формулах = {}".format(self.formulas_len))
        echo("Количество групп = {}".format(len(self.groups_childs.keys())))
        echo("Количество массивов = {}".format(self.arrays.Count))
        echo("Количество текстовых элеметов = {}".format(self.text_element.Count))
        echo("Количество заливок и маскировок = {}".format(self.filled_regions.Count))
        echo("Количество контроллеров = {}".format(self.controls.Count))
        echo("Количество тел выдавливания = {}".format(self.geometry.Count))
        echo("")

    def add_to_json(self, obj):
        for i in self._json_obj.keys():
            self._json_obj[i] += obj[i]

    @property
    def geometry(self):
        self._geometry = self.get_elements_by_cats(self.extrusion_cats).ToElementIds()
        self.remove_copyes(self._geometry)
        return self._geometry


    def check_profile_family(self):
        for i in self.geometry:
            if hasattr(i, "ProfileSymbol") and i.ProfileSymbol:
                self.__class__.analys_symbols([i.ProfileSymbol.Profile.Id], doc=self.doc, parent=self)

    def get_elements_by_cats(self, classes):
        els = None
        for i in classes:
            if els is None:
                els = FilteredElementCollector(self.doc).OfClass(i)
            else:
                els.UnionWith(FilteredElementCollector(self.doc).OfClass(i))
        return els


    @property
    def formulas_len(self):
        # meta_templ_params = "(^({0})[^A-Za-zА-Яа-я0-9_])|([^A-Za-zА-Яа-я0-9_]({0})[^A-Za-zА-Яа-я0-9_])|(({0})$)|(\[({0})\])"
        # templ_params = [meta_templ_params.format(i.Definition.Name) for i in self.parameters]
        # templ_params = re.compile("|".join(templ_params))

        operator_templ = "\*|\-|\/|\+\>\<\=\^"
        operator_templ = re.compile(operator_templ)

        func_templ = "roundup\(|sin\(|cos\(|tan\(|asin\(|acos\(|asin\(|atan\(|exp\(|abs\(|pi\(\)|log\(|sqrt\(|round\(|rounddown\(|not\(|and\(|or\(|if\("
        func_templ = re.compile(func_templ)

        form_len = 0
        for param in self.parameters:
            if param.IsDeterminedByFormula:
                # form_len += len(tuple(templ_params.finditer(param.Formula)))
                form_len += len(tuple(operator_templ.finditer(param.Formula)))
                form_len += len(tuple(func_templ.finditer(param.Formula)))

        return form_len


Family_Complex(doc, analis_instance=True)
