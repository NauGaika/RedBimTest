# -*- coding: utf-8 -*-

import re
from Autodesk.Revit.DB import ParameterType, Transaction
from common_scripts import *


class Precast_json_template(object):
    @property
    def all_dict_parameters(self):
        if not hasattr(self, "_all_dict_parameter"):
            el = self.element
            len_param_types = [
                ParameterType.Length,
                ParameterType.ReinforcementLength,
                ParameterType.BarDiameter]
            all_parameters = list(el.Parameters)
            if el.GetTypeId():
                all_parameters += list(el.Symbol.Parameters)
            all_parameters = {i.Definition.Name: to_mm(i.AsDouble(
            )) for i in all_parameters
                if i.Definition.ParameterType in len_param_types}
            self._all_dict_parameter = all_parameters
        return self._all_dict_parameter

    def get_re_template(self, parse_string):
        "Создает паттерн для поиска всех необходимых параметров."
        if not hasattr(self, "_re_template"):
            meta_templ_params = "(^({0})[^A-Za-zА-Яа-я0-9_\.])|([^A-Za-zА-Яа-я0-9_\.]({0})[^A-Za-zА-Яа-я0-9_\.])|([^A-Za-zА-Яа-я0-9_\.]({0})$)|(\[({0})\])|(^({0})$)"
            templ_params = [meta_templ_params.format(
                i) for i in self.all_dict_parameters.keys() if i in parse_string]
            templ_params = "|".join(templ_params)
            templ_params += "|(\*)|(\-)|(\/)|(\+)"
            templ_params += "|([^A-Za-zА-Яа-я_][0-9\.]+[^A-Za-zА-Яа-я_])|(^[0-9\.]+[^A-Za-zА-Яа-я_])|([^A-Za-zА-Яа-я_][0-9\.]+$)"
            templ_params = re.compile(templ_params)
            self.templ_params = templ_params
        return self.templ_params

    @property
    def json(self):
        if not hasattr(self, "_json"):
            self._json = None
            element = self.element
            params = self.all_dict_parameters
            if element.GetTransform().BasisY.Z > 0 or element.GetTransform().BasisY.IsAlmostEqualTo(element.FacingOrientation):
                par_name = "JSON_Template"
            else:
                par_name = "JSON_Template_Reflect"
            json_template = element.LookupParameter(par_name)

            if not json_template:
                json_template = element.Symbol.LookupParameter(par_name)
            if not json_template:
                echo("Не определен параметр JSON_Template")
            if json_template:
                json_template = json_template.AsString()

                field_need_to_calculate = []
                templ = re.compile("{{([^}}]+)")
                string_to_parses = templ.findall(json_template)

                all_is_good = True
                json_result = json_template
                self._json = json_template
                for string_to_parse in string_to_parses:
                    reg_templ = self.get_re_template(string_to_parse)
                    define_calculate_elements = reg_templ.findall(
                        string_to_parse)
                    operators = []
                    for finded_calculste_elements in define_calculate_elements:
                        finded_calculste_elements = [
                            calculate_element for calculate_element in finded_calculste_elements if calculate_element]
                        current_parameter = None
                        for i in finded_calculste_elements:
                            if current_parameter is None or i.strip() != current_parameter:
                                current_parameter = i.strip()
                                operators.append(current_parameter)
                    temp_str = string_to_parse
                    is_all_parameter_in_string = False
                    for oper in operators:
                        temp_str = temp_str.replace(oper, "", 1)
                    is_all_parameter_in_string = not bool(temp_str.strip())

                    if not is_all_parameter_in_string:
                        all_is_good = False
                        echo("Не разобрана строка \"{}\" в ней остались параметры \"{}\" в элементе {}".format(
                            string_to_parse, temp_str, self))
                    else:
                        resalt_calc = 0
                        result_string = ""
                        first_iter = True
                        next_operation = None
                        for i in operators:
                            if i not in "+-/*":
                                if i.replace(".", "").isdigit():
                                    val = float(i)
                                    result_part_string = " {}".format(i)
                                else:
                                    is_param = True
                                    val = params[i]
                                    result_part_string = "{}({})".format(
                                        i, val)
                                if next_operation is None:
                                    resalt_calc = val

                                elif next_operation == "+":
                                    resalt_calc += val

                                elif next_operation == "-":
                                    resalt_calc -= val

                                elif next_operation == "*":
                                    resalt_calc *= val

                                elif next_operation == "/":
                                    resalt_calc /= val
                            else:
                                next_operation = i
                                result_string += "{} {} ".format(
                                    result_part_string, i)
                        result_string += result_part_string
                        result_string = result_string + \
                            " = " + str(resalt_calc)
                        val_to_replace = "\"{{" + string_to_parse + "}}\""
                        json_result = json_result.replace(
                            val_to_replace, str(resalt_calc), 1)
                        self._json = json_result
            # echo(self.json)
        return self._json
