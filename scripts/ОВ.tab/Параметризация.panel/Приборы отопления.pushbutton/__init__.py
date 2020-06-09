from Autodesk.Revit.DB import BuiltInCategory, BuiltInParameter, Transaction, FilteredElementCollector, FamilyInstance, Options, BooleanOperationsType, BooleanOperationsUtils, Solid, ModelPathUtils, BuiltInParameterGroup
from Autodesk.Revit.DB.Mechanical import Space
from Autodesk.Revit.UI import FileOpenDialog
from io import open
import csv
import time
import json

curdoc = __revit__.ActiveUIDocument.Document
app = __revit__.Application
category = [BuiltInCategory.OST_MechanicalEquipment, BuiltInCategory.OST_PlumbingFixtures]
category = [curdoc.Settings.Categories.get_Item(i).Name for i in category]
selection = [curdoc.GetElement(elId) for elId in __revit__.ActiveUIDocument.Selection.GetElementIds()]
selection = filter(lambda el: el.Category.Name in category, selection)
selection = filter(lambda el: el.GetParameters("BDS_Class")[0].AsString() in ["Радиаторы", "Конвекторы"], selection)


class RB_Radiator:
    all_spaces = set()
    view_option = Options()
    all_radiators = []
    csv_data = None
    guids = None
    message = []

    def __init__(self, radiator):
        self.all_radiators.append(self)
        self.radiator = radiator
        self._space = None
        self.info = False
        self._random_line = None
        self._geom = None
        if self.space:
            self.space_number = None
            self.symbol = None
            self.length = None
            self.diameter = None
            self.producer = None
            self.description = None
            self.get_radiator_info()
        else:
            self.__class__.message.append("Для конвектора с id {} не найдено пространство в таблице".format(self.radiator.Id))

    def get_radiator_info(self):
        for i in self.csv_data:
            if to_str(i[1]).lower().strip() == to_str(self.space.space.Number).lower().strip():
                self.riser = i[0]
                self.space_number = i[1]
                self.symbol = to_str(i[2])
                try:
                    self.length = float(to_str(i[3]).replace(",", ".")) / 0.3048
                    self.diameter = float(to_str(i[4]).replace(",", ".")) / 0.3048 / 1000
                except ValueError:
                    self.__class__.message.append("Для конвектора с id {} в пространстве {} не заданы длина или диаметр \n".format(self.radiator.Id, self.space_number))
                    self.length = float()
                    self.diameter = float()
                self.producer = to_str(i[5])
                self.description = to_str(i[6])
                try:
                    # echo(i[7])
                    self.clap = float(to_str(i[7]).replace(",", "."))
                except ValueError:
                    self.__class__.message.append("Для конвектора с id {} в пространстве {} не найдены настройки клапана \n".format(self.radiator.Id, self.space_number))
                    self.clap = float(0)
                self.info = True
                break
        # else:
            # self.__class__.message += "Для конвектора с id {} не найдены настройки в таблице \n".format(self.radiator.Id)
        if self.info:
            self.csv_data.remove(i)
        

    @property
    def space(self):
        if self._space is None:
            for space in self.all_spaces:
                if self._space:
                    break
                for space_geometry in space.geometry:
                    # echo("Ищем радиатор через линию")
                    if self._space:
                        break
                    l_c = 0
                    for i in self.random_line:
                        l_c += 1
                        res = space_geometry.IntersectWithCurve(i, None)
                        if res.SegmentCount:
                            self._space = space
                            # self.__class__.message.append("Найдено через линии {} \n".format(l_c))
                            break
                    # else:
                    #     echo("Все плохо")
                        # for cur_geometry in self.geometry:
                        #     sum_area = 0
                        #     if self._space:
                        #         break
                        #     union_solid = BooleanOperationsUtils.ExecuteBooleanOperation(cur_geometry, space_geometry, BooleanOperationsType.Union)
                        #     sum_area += ((cur_geometry.SurfaceArea + space_geometry.SurfaceArea) - union_solid.SurfaceArea)
                        #     if sum_area > 0.0001:
                        #         self._space = space
                        #         echo("Найдено через объем")
                        #         break
            # else:
            #     echo("Не найдено")
            if self._space:
                self._space.radiators -= 1
        return self._space

    @property
    def geometry(self):
        if self._geom is None:
            geom = list(list(self.radiator.Geometry[self.view_option].GetEnumerator())[0].GetInstanceGeometry().GetEnumerator())
            self._geom = filter(lambda el: isinstance(el, Solid) and el.Volume > 0, geom)
        return self._geom

    @property
    def random_line(self):
        if self._random_line is None:
            self._random_line = set()
            tt = 0
            for g in self.geometry:
                if tt > 10:
                    break
                for i_c in range(g.Edges.Size):
                    if tt > 10:
                        break
                    tt += 1
                    i = g.Edges.Item[i_c].AsCurve()
                    self._random_line.add(i)
        return self._random_line

    def set_parameter(self, parameter, value):
        p = self.radiator.get_Parameter(self.guids[parameter])
        if p:
            if not p.IsReadOnly:
                p.Set(value)
            else:
                self.__class__.message.append("Параметр {} заблокирован у элемента с id {}".format(parameter, self.radiator.Id))
        else:
            self.__class__.message.append("Параметр {} не найден у элемента с id {}".format(parameter, self.radiator.Id))

    def set_parameters(self):
        if self.info:
            self.set_parameter("BS_Изготовитель", self.producer)
            self.set_parameter("BS_Наименование", self.description)
            self.set_parameter("MEP_Габаритная длина", self.length)
            self.set_parameter("BS_Маркировка", self.symbol)
            self.set_parameter("MEP_Стояк_номер", self.riser)
            self.set_parameter("OV_Номер пространства", self.space_number)
            self.set_parameter("MEP_Диаметр 1", self.diameter)
            self.set_parameter("OV_Настройка клапана", self.clap)


class RB_Space:
    all_space = []
    view_option = Options()
    all_spaces_numbers = None
    all_spaces_numbers_set = None

    def __init__(self, space):
        self._geometry = None
        self.all_space.append(self)
        self.space = space
        self.radiators = self.all_spaces_numbers.count(self.space.Number)
        self.all_spaces_numbers_set.discard(self.space.Number)

    @property
    def geometry(self):
        if self._geometry is None:
            self._geometry = list(self.space.Geometry[self.view_option].GetEnumerator())
        return self._geometry


class Radiator_Parametrization:
    _all_space = []
    _all_radiators = []
    _parameter_dict = {}

    def __init__(self, data):
        self.csv_data = data
        RB_Space.all_spaces_numbers = [i[1] for i in self.csv_data]
        RB_Space.all_spaces_numbers_set = set([i[1] for i in self.csv_data])
        RB_Radiator.guids = self._parameter_dict
        RB_Radiator.csv_data = data
        RB_Radiator.all_spaces = set(self.all_spaces)  # записываем все пространства в класс конвекторов
        self.all_radiators # Создаем все конвекторы

    @property
    def all_spaces(self):
        if not self._all_space:
            self._all_space = FilteredElementCollector(curdoc).OfCategory(BuiltInCategory.OST_MEPSpaces).ToElements()
            self._all_space = [RB_Space(i) for i in self._all_space if i.Volume]
            self._all_space = [i for i in self._all_space if i.radiators]
        return self._all_space

    @property
    def all_radiators(self):
        if not self._all_radiators:
            if not selection:
                self._all_radiators = list(FilteredElementCollector(curdoc).OfCategory(BuiltInCategory.OST_MechanicalEquipment).OfClass(FamilyInstance).ToElements())
                self._all_radiators += list(FilteredElementCollector(curdoc).OfCategory(BuiltInCategory.OST_PlumbingFixtures).OfClass(FamilyInstance).ToElements())
                new_arr = []
                for i in self._all_radiators:
                    p = i.GetParameters("BDS_Class")
                    if p:
                        p = p[0].AsString()
                        if p == "Конвекторы" or p == "Радиаторы":
                            new_arr.append(i)
                self._all_radiators = new_arr
            else:
                self._all_radiators = selection
            new_arr = []
            cur_time = 0
            for i in self._all_radiators:
                if time.time() - cur_time > 30:
                    cur_time = time.time()
                    echo("{}/{}".format(len(new_arr), len(self._all_radiators)))
                new_arr.append(RB_Radiator(i))
            self._all_radiators = new_arr
        return self._all_radiators

    def set_radiator_parameter_to_revit(self):
        with Transaction(curdoc, 'Параметризация конвекторов') as t:
            t.Start()
            for i in self.all_radiators:
                i.set_parameters()
            t.Commit()

    def check_spaces(self):
        for i in RB_Space.all_spaces_numbers_set:
            echo("Не найдено пространств с номером {}".format(i))
        for i in self.all_spaces:
            if i.space.Number in i.all_spaces_numbers:
                if i.radiators > 0:
                    echo("В пространстве с номером {} id {} не хватает {} конвектор или для них не заполнен BDS_Class".format(i.space.Number, i.space.Id, i.radiators))
                elif i.radiators < 0:
                    echo("В пространстве с номером {} id {} лишний {} конвектор".format(i.space.Number, i.space.Id, i.radiators * -1))
            else:
                echo("Пространства {} с id {} нет в таблице".format(i.space.Number, i.space.Id))

    @classmethod
    def check_parameters(cls):
        category = [BuiltInCategory.OST_MechanicalEquipment, BuiltInCategory.OST_PlumbingFixtures]
        category = [curdoc.Settings.Categories.get_Item(i) for i in category]
        params = {
            "BS_Изготовитель": BuiltInParameterGroup.PG_TEXT,
            "BS_Наименование": BuiltInParameterGroup.PG_TEXT,
            "MEP_Габаритная длина": BuiltInParameterGroup.PG_GEOMETRY,
            "BS_Маркировка": BuiltInParameterGroup.PG_TEXT,
            "MEP_Стояк_номер": BuiltInParameterGroup.PG_TEXT,
            "OV_Номер пространства": BuiltInParameterGroup.PG_TEXT,
            "MEP_Диаметр 1": BuiltInParameterGroup.PG_GEOMETRY,
            "OV_Настройка клапана": BuiltInParameterGroup.PG_MECHANICAL}
        shared_par_file = app.OpenSharedParameterFile()
        pb = curdoc.ParameterBindings
        with Transaction(curdoc, "Добавление недостающих параметров") as t:
            t.Start()
            for i in shared_par_file.Groups:
                for b in i.Definitions:
                    if b.Name in params.keys():
                        cls._parameter_dict.update({b.Name: b.GUID})
                        if pb.Contains(b):
                            parameter_bind = pb.Item[b]
                            change_cats = []
                            for cat in category:
                                if not parameter_bind.Categories.Contains(cat):
                                    parameter_bind.Categories.Insert(cat)
                                    change_cats.append(cat.Name)
                            if change_cats:
                                echo("Для параметра {} добавлены категории {}".format(b.Name, ", ".join(change_cats)))
                                pb.ReInsert(b, parameter_bind)
                        else:
                            cat_set = app.Create.NewCategorySet()
                            for cat in category:
                                cat_set.Insert(cat)
                            nib = app.Create.NewInstanceBinding(cat_set)
                            pb.Insert(b, nib, params[b.Name])
                            echo("Добавлен параметр {}".format(b.Name))
            t.Commit()


try:
    if selection:
        message("Параметризация производится для выбранного оборудования в количестве {}".format(len(selection)))
    message("Выберете файл с Итогами отопительных приборов в формате csv")
    dialog = FileOpenDialog("Файл CSV (*.csv;)|*.csv")
    dialog.Show()
    mpath = dialog.GetSelectedModelPath()
    if mpath is None:
        raise SystemError("Не выборан файл с Итогами отопительных приборов")
    path = ModelPathUtils.ConvertModelPathToUserVisiblePath(mpath)

    with open(path, 'rt', encoding="maccyrillic") as file:
        data = csv.reader(file, delimiter=';')
        data = [i for i in data]
        for k in range(len(data)):
            if data[k][0].isdigit():
                break
        data = data[2:]
        file.close()

    dialog = FileOpenDialog("Файл CSV (*.csv;)|*.csv")
    dialog.Show()
    mpath = dialog.GetSelectedModelPath()
    if mpath is None:
        raise SystemError("Не выборан файл с Итогами настройки")
    path = ModelPathUtils.ConvertModelPathToUserVisiblePath(mpath)
    with open(path, 'rt', encoding="maccyrillic") as file:
        data_2 = csv.reader(file, delimiter=';')
        data_2 = [i for i in data_2]
        file.close()
        start_time = time.time()
        for i in data:
            b = None
            for b in data_2:
                if b[0] == i[1]:
                    el = b[1].replace(",", ".")
                    if el.replace(".", "1").isdigit():
                        i[7] = float(el)
                    break
            if b:
                data_2.remove(b)
    Radiator_Parametrization.check_parameters()
    el = Radiator_Parametrization(data)
    el.set_radiator_parameter_to_revit()
    if not selection:
        el.check_spaces()
    echo(RB_Radiator.message)
    echo("Потребовалось {} сек для обработки {} пространств и {} приборов".format(time.time() - start_time, len(el.all_spaces), len(el.all_radiators)))
except SystemError as res:
    message(res.args[0])
