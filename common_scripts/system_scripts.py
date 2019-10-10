# -*- coding: utf-8 -*-

import sys, urllib, clr
clr.AddReference('System')
clr.AddReference('System.Windows')
clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Drawing')
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
from System.Windows.Forms import MessageBox
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
            if not isinstance(i, list):
                i = [i]
            for b in i:
                string = to_str(b) + '\n\r'
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
    return round(mm/0.00328084)

def get_parameter(el, parameter_name, is_dict=False, for_set=False):
    is_mm_list = [ParameterType.Length, ParameterType.ReinforcementLength, ParameterType.BarDiameter]
    doc = __revit__.ActiveUIDocument.Document
    all_parameters = list(el.Parameters)
    val_to_ret = None
    if el.GetTypeId():
        all_parameters += list(doc.GetElement(el.GetTypeId()).Parameters)
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
    
__all__ = ['echo', 'echo_dir', 'to_str', 'echo_close', 'to_feet', 'to_mm', 'get_parameter', 'message']
