from Autodesk.Revit.DB import Transaction,\
    FilteredElementCollector, BuiltInCategory, ElementId,\
    RevitLinkInstance
from Autodesk.Revit.DB import ParameterType
from common_scripts.RB_Scheduled import RB_Scheduled
from common_scripts import echo
import re

from System.Collections.Generic import List

import csv
import os
import json
from io import open
__revit__ = __revit__
uidoc = __revit__.ActiveUIDocument
# curview = uidoc.ActiveGraphicalView
doc = uidoc.Document

par_names = {
    "КлассЧисло": ("Арм.КлассЧисло", False),
    "Материал": ("Материал несущих конструкций", False),
    "МатериалИмя": ("Мтрл.Название", True),
    "Подсчет": ("О_Материал тип подсчета", False),
    "Количество": ("О_Количество", False),
    "МассаПМ": ("О_МассаПогМетра", False),
    "Длина": ("Рзм.Длина", False),
    "Площадь": ("Рзм.Площадь", False),
    "Объем": ("Рзм.Объем", False),
    "Масса": ("О_Масса", False),
    "МатериалОбъем": ("Объем", False),
    "МатериалПлощадь": ("Площадь", False),
    "МатериалПлотность": ("BDS_Density", True),
    "ГруппаВРС": ("Арм.ГруппаВРС", False),
    "КлассЧисло_2": ("Precast_SteelFormula", False)
}

csv_path = os.path.join(file_path, "summon.csv")


class StructuralFraming(object):
    summary_structure = {
        "elements": {},
        "rows": set()
    }

    def __init__(self, el, csv_dict, count=1):
        self.error = False
        # echo(self)
        self.file_path = file_path
        self.count = count
        self.csv = csv_dict
        self.el = el
        # echo(self["МатериалИмя"])
        self.name, self.gost, self.weight = self.get_parameters_from_csv()
        if self.name and self.gost:
            if self.element_type != 5:
                self.mass = self.calculate_mass()
                # echo(self.name, self.mass)
                self.add_to_summary_structure()
        else:
            self.error = "{} отсутствует в сортаменте Арм.КлассЧисло {}".format(
                self, self.class_number)

    def doc_name(self):
        return self.el.Document.Title

    def __repr__(self):
        return "{} {} ".format(self.el.Symbol.Family.Name, self.el.Id)

    def __getitem__(self, key):
        par = self.get_param(key)
        if par:
            if par.Definition.ParameterType == ParameterType.Number:
                return par.AsDouble()
            elif par.Definition.ParameterType == ParameterType.Currency:
                return par.AsDouble()
            elif par.Definition.ParameterType == ParameterType.Text:
                return par.AsString()
            elif par.Definition.ParameterType == ParameterType.Integer:
                return par.AsInteger()
            elif par.Definition.ParameterType == ParameterType.Length:
                return par.AsDouble() * 304.8
            elif par.Definition.ParameterType == ParameterType.Area:
                return par.AsDouble() * (304.8**2)
            elif par.Definition.ParameterType == ParameterType.Volume:
                return par.AsDouble() * (304.8**3)

    def get_parameters_from_csv(self):
        self.class_number = self[par_names["КлассЧисло_2"]]
        if self.class_number:
            self.class_number = self.calculate_class_number(self.class_number)
            # echo("КлассЧисло {} у {}".format(class_number, self))
        else:
            self.class_number = self[par_names["КлассЧисло"]]
            # echo("{} Не найдено у {}".format(
                # par_names["КлассЧисло_2"][0], self))
        gost = None
        weight = None
        name = None
        # echo(self.el.Name, class_number, type(class_number))
        self.class_number = str(self.class_number) if str(
            self.class_number) in self.csv.keys() else str(int(self.class_number))
        if self.class_number in self.csv.keys():
            name = self.csv[self.class_number][0]
            gost = self.csv[self.class_number][1]
            weight = self.csv[self.class_number][2]
        return name, gost, weight

    @property
    def element_type(self):
        return self["BDS_ElementType"]
    
    def calculate_class_number(self, str_to_parse):
        meta_templ_params = "([^A-Za-zА-Яа-я_][0-9\.]+[^A-Za-zА-Яа-я_])|(^[0-9\.]+[^A-Za-zА-Яа-я_])|([^A-Za-zА-Яа-я_][0-9\.]+$)|((\*)|(\-)|(\/)|(\+))|([А-Яа-яA-Za-z\._]+)"
        meta_templ_params = re.compile(meta_templ_params)
        params = [[j for j in i if j][0].strip()
                  for i in meta_templ_params.findall(str_to_parse)]
        multiple = []
        for key, par in enumerate(params):
            if par == "*" or par == "/":
                multiple.append(
                    (key - 1, key, key + 1, params[key-1], par, params[key+1]))
        for i in multiple:
            # echo(i)
            if i[4] == "*":
                res = self.get_param_or_float(
                    i[3]) * self.get_param_or_float(i[5])
            elif i[4] == "/":
                res = self.get_param_or_float(
                    i[3]) / self.get_param_or_float(i[5])
            params[i[1]] = res
            params[i[0]] = None
            params[i[2]] = None
        params = [i for i in params if i is not None]
        result = 0
        for key, i in enumerate(params):
            if key == 0:
                result = i
            elif i == "+":
                result += self.get_param_or_float(params[key+1])
            elif i == "-":
                result -= self.get_param_or_float(params[key+1])
        return result

    def get_param_or_float(self, par):
        if isinstance(par, float):
            return par
        if par.replace(".", "").isdigit():
            return float(par)
        return self[par]

    def add_to_summary_structure(self):
        gs = self.summary_structure["elements"]
        is_arm = self["КлассЧисло"] // 100000000000 == 2
        type_col = "Изделия арматурные" if is_arm else "Изделия закладные"
        if type_col not in gs.keys():
            gs[type_col] = {
                "elements": {},
            }
        ss = gs[type_col]["elements"]

        if self["МатериалИмя"] not in ss.keys():
            ss[self["МатериалИмя"]] = {
                "elements": {}
            }
        mat_dict = ss[self["МатериалИмя"]]["elements"]
        if self.gost not in mat_dict.keys():
            mat_dict[self.gost] = {
                "elements": {}
            }
        gost_dict = mat_dict[self.gost]["elements"]

        if self.name not in gost_dict.keys():
            gost_dict[self.name] = {
                "elements": {}
            }
        name_dict = gost_dict[self.name]["elements"]

        group_vrs = self["ГруппаВРС"]
        if group_vrs not in name_dict.keys():
            self.summary_structure["rows"].add(group_vrs)
            name_dict[group_vrs] = 0
        name_dict[group_vrs] += self.mass

    def calculate_mass(self):
        """
        Подсчет массы.

        Считается по формулам описанным
        https://docs.google.com/spreadsheets/d/1qB8FUkEdyUgw6qt5sLppX-QyvMNmKUa-83KUxZC5I0E/edit?usp=sharing

        В случае ошибки выводит сообщение
        """
        calc_type = self[par_names["Подсчет"]]
        mass = 0
        try:
            if calc_type:
                calc_type = calc_type % 100
                if calc_type == 1:
                    mass = self["Количество"] * \
                        self["МассаПМ"]
                elif calc_type == 2:
                    mass = self["Количество"] * \
                        self["МассаПМ"] * \
                        self["Длина"] / 1000
                elif calc_type == 3:
                    mass = self["Количество"] * \
                        self["МассаПМ"] * \
                        self["Площадь"] / 1000**2
                elif calc_type == 4:
                    mass = self["Количество"] * \
                        self["МассаПМ"] * \
                        self["Объем"] / 100**3
                elif calc_type == 5:
                    mass = self["Количество"] * \
                        self["Масса"]
                elif calc_type == 6:
                    mass = self["Количество"]
                elif calc_type == 12:
                    mass = self["МатериалОбъем"] / 1000**3 * \
                        self["МатериалПлотность"]
        except:
            echo("Ошибка в подсчете массы, {}".format(self))
        return mass

    def get_param(self, param_tuple):
        if isinstance(param_tuple, str):
            if param_tuple in par_names.keys():
                param_tuple = par_names[param_tuple]
            else:
                param_tuple = param_tuple, False
        param, is_material = param_tuple
        el = self.el
        if not hasattr(self, "_all_parameters"):
            self._all_parameters = {}
        if param not in self._all_parameters.keys():
            if is_material:
                mat = el.LookupParameter(par_names["Материал"][0])
                mat = mat if mat is not None else el.Symbol.LookupParameter(
                    par_names["Материал"][0])
                if mat:
                    el = el.Document.GetElement(mat.AsElementId())
            par = el.LookupParameter(param)
            if not par:
                par = el.Symbol.LookupParameter(param)
            self._all_parameters[param] = par
        return self._all_parameters[param]


class ElementFinder(object):
    def __init__(self, __revit__, csv_path):
        """
        Иниацилизация поисковика.

        в self.docs все документы, в которых ищем каркас несущий.
        в self.structural_framing все элементы каркаса несущего
        """
        self.__revit__ = __revit__
        # echo(self.docs)
        self.csv_dict = self.open_csv(csv_path)
        self.structural_framing
        # echo(len(self.structural_framing))
        self.csv_path = csv_path
        self.make_schedule(StructuralFraming.summary_structure)

    @property
    def docs(self):
        """
        Получаем все документы.

        Получаем все экземпляры связей
        Записываем их в словарь self._docs
        Указываем их количество.
        """
        if not hasattr(self, "_docs"):
            self._docs = {}
            cur_doc = self.__revit__.ActiveUIDocument.Document
            docs = FilteredElementCollector(cur_doc).OfClass(RevitLinkInstance).ToElements()
            for doc in docs:
                if doc.GetLinkDocument():
                    g_doc = doc.GetLinkDocument()
                    self._docs.setdefault(g_doc, 0)
                    self._docs[g_doc] += 1
        return self._docs

    def make_schedule(self, el_dict):
        """
        Создание спецификации на основе словаря.

        1. Посчитать количество столбцов
        Берем count из el_dict самого верхнего элемента и прибаляем 1
        2. Создать Cоостветствующее количество строк из el_dict["rows"]
        """
        # echo(column_count)
        sched = RB_Scheduled(__revit__.ActiveUIDocument.ActiveGraphicalView)
        sched.remove_all_row_and_column()
        rows_names = list(el_dict["rows"])
        # Подсчитать ширины строчек проитиерировавшись по всему словарю
        column_width = [50]
        for steel_mark_dict in el_dict["elements"].values():
            for element_type_dict in steel_mark_dict["elements"].values():
                for gost_dict in element_type_dict["elements"].values():
                    for name_dict in gost_dict["elements"].values():
                        column_width.append(15)
                    column_width.append(15)
                column_width.append(20)
        column_width.append(20)

        sched.set_table_width(sum(column_width))
        sched.set_column_count(len(column_width))
        sched.set_columns_width(column_width)
        sched.add_rows(0, 5 + len(rows_names))
        sched.merge_cell(0, 0, len(column_width)-1, 0)
        sched.set_cell_border(0, 0, False, False, False, True)
        sched.set_row_val(0, 0, "Ведомость расхода стали, кг")
        gen_sum = 0
        end = 1
        vrs_elements = {}
        for element_type, element_type_dict in el_dict["elements"].items():
            start_type = end
            steel_mark_sum = 0
            for steel_mark, steel_mark_dict in element_type_dict["elements"].items():
                start_steel = end
                for gost, gost_dict in steel_mark_dict["elements"].items():
                    gost_sum = 0
                    start_gost = end
                    for name, name_dict in gost_dict["elements"].items():
                        for vrs, vrs_sum in name_dict["elements"].items():

                            vrs_elements.setdefault(vrs, len(vrs_elements))
                            pos = vrs_elements[vrs] + 5
                            vrs_sum = round(vrs_sum, 2)
                            sched.set_row_val(end, pos, vrs_sum)
                            sched.set_row_val(0, pos, vrs)
                            steel_mark_sum += vrs_sum
                            gost_sum += vrs_sum
                            gen_sum += vrs_sum
                        sched.set_row_val(end, 4, name)
                        end += 1
                    sched.set_row_val(end, 4, "Итого")
                    sched.set_row_val(end, pos, gost_sum)
                    sched.merge_cell(start_gost, 3, end, 3)
                    sched.set_row_val(start_gost, 3, gost)
                    end += 1
                sched.set_row_val(start_steel, 2, steel_mark)
                sched.set_row_val(end, 2, "Всего")
                sched.set_row_val(end, pos, steel_mark_sum)
                sched.merge_cell(end, 2, end, 4)
                sched.merge_cell(start_steel, 2, end-1, 2)
                end += 1
            sched.merge_cell(start_type, 1, end-1, 1)
            sched.set_row_val(start_type, 1, element_type)
        sched.merge_cell(end, 1, end, 4)
        sched.set_row_val(end, 1, "Общий расход")
        sched.set_row_val(end, pos, gen_sum)

        sched.merge_cell(0, 1, 0, 4)

    @property
    def structural_framing(self):
        if not hasattr(self, "_structural_framing"):
            eror_elements = []
            self._structural_framing = []
            for doc, count in self.docs.items():
                fec = FilteredElementCollector(doc).OfCategory(
                    BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType()
                for el in fec.ToElements():
                    par = self.get_parameter(el, par_names["КлассЧисло"])
                    if par and par.AsDouble():
                        new_el = StructuralFraming(el, self.csv_dict, count=count)
                        if not new_el.error:
                            self._structural_framing.append(new_el)
                        else:
                            eror_elements.append(new_el)
            if len(eror_elements):
                echo("Ошибочные элементы в проекте в количестве {}.".format(len(eror_elements)))
            for i in eror_elements:
                echo(i.error, " ", i.doc_name())
        return self._structural_framing

    def get_parameter(self, element, parameter):
        parameter_val = element.LookupParameter(parameter[0])
        parameter_val = element.Symbol.LookupParameter(
            parameter[0]) if parameter_val is None else parameter_val
        return parameter_val

    def open_csv(self, path):
        res = {}
        with open(path, encoding='utf-8', errors="ignore") as f:
            lines = [i.strip() for i in f.read().split("\n")]
            lines = [i.split(";") for i in lines]
            res = {i[0]: i[1:] for i in lines}
        return res


with Transaction(doc, "Сформировать ВРС") as t:
    t.Start()
    ElementFinder(__revit__, csv_path)
    t.Commit()
