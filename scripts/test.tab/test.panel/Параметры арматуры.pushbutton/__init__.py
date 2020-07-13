import re
import json
from Autodesk.Revit.DB import Transaction, FilteredElementCollector, BuiltInCategory, ParameterType
from Autodesk.Revit.DB.Structure import Rebar, RebarInSystem
from common_scripts import echo


class RebarParametrization(object):
    """Выполняет запись параметров арматуры по JSON."""
    all_rebars = []
    parameter_code = "BDS_ReinforcementCode"

    def __init__(self, el, is_echo=False):
        "Создание экземпляр элемента параметризации."
        self.is_echo = is_echo
        self.element = el
        if isinstance(el, Rebar) or isinstance(el, RebarInSystem):
            pass
        else:
            pass
        par_code = self[self.parameter_code]
        if par_code:
            all_str = self.find_str_to_parse(self[self.parameter_code])
            for i in all_str:
                prev_val = "'{{" + i + "}}'"
                new_val = self.calculate_symbol(i)
                new_val = new_val if isinstance(new_val, str) else str(new_val)
                par_code = par_code.replace(prev_val, new_val)
            par_code = par_code.replace("'", '"')
            try:
                if self.is_echo:
                    echo(json.loads(par_code))
            except:
                if self.is_echo:
                    echo("Ошибка формирования json {}".format(self))
            self["BDS_ReinforcementSymbol"] = par_code

    def __repr__(self):
        return str(self.element.Id)

    def find_str_to_parse(self, str_to_parse):
        """
        Находим элементы, которые нужно распарсить.

        Все они должны быть обрамлены {{ то, что нужно распарсиь}}

        На вход текст параметра.
        """
        templ = re.compile("{{([^}}]+)")
        return templ.findall(str_to_parse)

    def calculate_symbol(self, str_to_parse):
        """
        Вычисления производимые в строках.

        Для начала находим все параметры регулярным выражением
        От параметров откидываем квадратные скобки.
        Заменяем пармаетры на числа
        Все числа преобразовываем из строки в float
        Находим все, что нужно умножить или поделить.

        В цикле выполняем умножение.
        То, что перемножили делаем None
        Результат записываем во втоой элемент
        Очищаем массив от None
        Как с умножением поступаем с сложением/вычитанием

        Возвращаем результат

        Если всего один элемент - возвращаем его
        """
        try:
            meta_templ_params = "([^A-Za-zА-Яа-я_][0-9\.]+[^A-Za-zА-Яа-я_])|(^[0-9\.]+[^A-Za-zА-Яа-я_])|([^A-Za-zА-Яа-я_][0-9\.]+$)|((\*)|(\-)|(\/)|(\+))|(\[[А-Яа-яA-Za-z\.\s_]+\])"
            meta_templ_params = re.compile(meta_templ_params)
            params = [[j for j in i if j][0].strip().lstrip("[").rstrip("]")
                      for i in meta_templ_params.findall(str_to_parse)]
            params = [(self[i] if self[i] else i) for i in params]
            params = [(float(i) if isinstance(i, str) and i.replace(".", "").isnumeric() else i) for i in params]
            multiple = []
            for key, par in enumerate(params):
                if par == "*" or par == "/":
                    multiple.append(
                        (key - 1, key, key + 1, params[key-1], par, params[key+1]))
            for i in multiple:
                if i[4] == "*":
                    res = i[3] * i[5]
                elif i[4] == "/":
                    res = i[3] / i[5]
                params[i[1]] = res
                params[i[0]] = None
                params[i[2]] = None
            params = [i for i in params if i is not None]
            result = 0
            for key, i in enumerate(params):
                if key == 0:
                    result = i
                elif i == "+":
                    result += params[key+1]
                elif i == "-":
                    result -= params[key+1]
            result = round(result) 
        except:
            result = '"ошибка"'
            if self.is_echo:
                echo("Ошибка в формировании параметра в {}".format(self))
        return result

    @classmethod
    def find_all_rebar(cls, uidoc):
        """
        Найти всю арматуру.

        Выполнить параметризацию арматурных стержней.
        """
        cls.doc = uidoc.Document
        if uidoc.Selection.GetElementIds().Count:
            els = [cls.doc.GetElement(i) for i in uidoc.Selection.GetElementIds()]
        else:
            els = FilteredElementCollector(cls.doc).\
                OfCategory(BuiltInCategory.OST_Rebar).\
                WhereElementIsNotElementType().ToElements()
        with Transaction(cls.doc, "Записать параметры арматуры") as t:
            t.Start()
            for el in els:
                rr = cls(el, is_echo=uidoc.Selection.GetElementIds().Count>0)
                cls.all_rebars.append(rr)
            t.Commit()

    def get_param(self, param):
        """
        Метод получения параметров из семейства.

        По умолчанию берется параметр у текущего элемента.

        """
        if not hasattr(self, "_all_parameters"):
            self._all_parameters = {}
        if param not in self._all_parameters.keys():
            par = self.element.LookupParameter(param)
            symb = self.doc.GetElement(self.element.GetTypeId())
            if not par and symb:
                par = symb.LookupParameter(param)
            self._all_parameters[param] = par
        return self._all_parameters[param]

    def __getitem__(self, key):
        """
        Получение параметра на основании имени параметра по индексу.

        Проверяется тип параметра и в зависимости от этого
        возвращается значение приведенное к метрическим значениям

        Если параметр не найдет - возвращается None
        """
        par = self.get_param(key)
        if par:
            if par.Definition.ParameterType == ParameterType.Number or\
                    par.Definition.ParameterType == ParameterType.Currency:
                return par.AsDouble()
            elif par.Definition.ParameterType == ParameterType.Text:
                return par.AsString()
            elif par.Definition.ParameterType == ParameterType.Integer:
                return par.AsInteger()
            elif par.Definition.ParameterType == ParameterType.Length or\
                    par.Definition.ParameterType == ParameterType.BarDiameter or\
                    par.Definition.ParameterType == ParameterType.ReinforcementLength:
                if par.Definition.ParameterType == ParameterType.ReinforcementLength:
                    return round(par.AsDouble() * 304.8)
                return par.AsDouble() * 304.8
            elif par.Definition.ParameterType == ParameterType.Area:
                return par.AsDouble() * (304.8**2)
            elif par.Definition.ParameterType == ParameterType.Volume:
                return par.AsDouble() * (304.8**3)
            elif par.Definition.ParameterType == ParameterType.Invalid:
                return par.AsValueString()

    def __setitem__(self, key, val):
        """
        Установка значения параметра по индексу.
        Если параметр не найдет
        """
        par = self.get_param(key)
        if par:
            par.Set(val)
        else:
            raise Exception("Параметр {} не найден у {}".format(key, self))



RebarParametrization.find_all_rebar(__revit__.ActiveUIDocument)