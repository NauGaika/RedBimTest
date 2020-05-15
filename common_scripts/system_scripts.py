# -*- coding: utf-8 -*-

import sys, urllib, clr
clr.AddReference('System')
clr.AddReference('System.Windows')
clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Drawing')
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')

from System.Windows.Forms import MessageBox, ProgressBar, Form
from System.Windows.Forms import Application, Form, ProgressBar
# from System.Threading import ThreadStart, Thread
# from IronPython.Runtime.Calls import CallTarget0

from Autodesk.Revit.DB import StorageType, ParameterType
from RB_print_class import RB_print

PRINTER = RB_print()

#Преобразует объект в строку
def to_str(obj):
    if isinstance(obj, str):
        return obj
    else:
        return str(obj)

#Выдает сообщение
def echo(*arg):
    if arg:
        string = ''
        for i in arg:
            if isinstance(i, dict):
                for k in i.keys():
                    string += to_str(k) + ' : ' + to_str(i[k]) + '\r\n'
            elif isinstance(i, list):
                for k in i:
                    string += to_str(k) + '\r\n'
            else:
                string += to_str(i)
        PRINTER.Show(string)
            # print(to_str(i))

def echo_arr(*arg):
    if arg:
        string = ''
        for i in arg:
            string = to_str(i) + '\n\r'
            PRINTER.Show(to_str(string))
            # print(to_str(i))

def echo_close():
    PRINTER.Close()


#возвращает родительскую папку заданной вложенности


def echo_dir(el):
    line = ''
    for i in el:
            line += to_str(i) + '\n\r'
    echo(line)

def to_feet(mm):
    return mm*0.00328084

def to_mm(mm):
    return round(mm/0.00328084, 3)

def get_parameter(el, parameter_name, is_dict=False, for_set=False):
    is_mm_list = [ParameterType.Length, ParameterType.ReinforcementLength, ParameterType.BarDiameter]
    all_parameters = list(el.Parameters)
    val_to_ret = None
    if el.GetTypeId():
        all_parameters += list(el.Symbol.Parameters)
    all_parameters = {i.Definition.Name: i for i in all_parameters}
    if parameter_name in all_parameters.keys():
        param = all_parameters[parameter_name]
        if for_set:
            return param
        if param.StorageType == StorageType.Double:
            if param.Definition.ParameterType in is_mm_list:
                val_to_ret = to_mm(param.AsDouble())
            else:
                val_to_ret = param.AsDouble()
        if param.StorageType == StorageType.Integer:
            if param.Definition.ParameterType == ParameterType.YesNo:
                val_to_ret = bool(param.AsInteger())
            else:
                val_to_ret = param.AsInteger()
        if param.StorageType == StorageType.String:
            val_to_ret = param.AsString()
    if is_dict:
        return {parameter_name: val_to_ret}
    return val_to_ret
    
def message(text):
    text = to_str(text)
    MessageBox.Show(text, 'RedBim')

class RB_Parameter_mixin:

    def __init__(self):
        super(RB_Parameter_mixin, self).__init__()

    @classmethod
    def get_parameter(cls, element, parameter):
        if not hasattr(cls, "_rb_parameters"):
            cls._rb_parameters = {}
        cls._rb_parameters.setdefault(element.Id.IntegerValue, {})
        cls._rb_parameters[element.Id.IntegerValue].setdefault(parameter, None)
        if cls._rb_parameters[element.Id.IntegerValue][parameter] is None:
            par = element.LookupParameter(parameter)
            if not par and element.GetTypeId():
                par = element.Symbol.LookupParameter(parameter)
            if par:
                cls._rb_parameters[element.Id.IntegerValue][parameter] = par
        return cls._rb_parameters[element.Id.IntegerValue][parameter]



__all__ = ['echo', 'echo_dir', 'to_str', 'echo_close', 'to_feet', 'to_mm', 'get_parameter', 'message', "RB_Parameter_mixin"]
