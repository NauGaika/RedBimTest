# coding: utf8
"""Добавляем необходимые фильтры для КЖ"""
import copy
__title__ = 'Перемаркировать стержни'
import os, clr, json, re
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent
from Autodesk.Revit.DB.Structure import Rebar
from System.Collections.Generic import List
from System.Windows.Forms import MessageBox


uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
curview = uidoc.ActiveGraphicalView
selection = [doc.GetElement(elId) for elId in __revit__.ActiveUIDocument.Selection.GetElementIds()]

class Rebar_remark:
    selection = List[ElementId]()
    all_rebars = []
    prefix_params = ['Арм_']
    if_ifc = 'Арм.ВыполненаСемейством'
    diameter_pag = {}
    round_n = 5
    k = True
    max_pos = 0
    _pass_numbers = []
    sorted_elems = []

    def __init__(self, rebar):
        """Создаем экземпляр арматуры."""
        self.rebar = rebar
        self.params = {}
        self.get_all_rebar_param()
        self.all_rebars.append(self)

    def __str__(self):
        return "{} {}".format(self.sort_parameter, self.litera)
    @property
    def litera(self):

        if 'Арм.ПрефиксФормы' in self.params:
            return self.params['Арм.ПрефиксФормы'][1]
        else:
            return ''
    
    @property
    def sort_parameter(self):

        calc_length = (
            self.round_n
            * round(self.get_param_ifc('Рзм.Длина', 'Длина стержня')
            / self.round_n)
            )

        calc_diam = self.get_param_ifc('Рзм.Диаметр', 'Диаметр стержня')
        like_pag = self.params['Рзм.ПогМетрыВкл'][1]
        if self.params['Арм.КлассЧисло'][1] > 0:
            a1 = 1000
        else:
            a1 = 1

        x1 = self.params['Арм.КлассЧисло'][1] * a1

        if like_pag:
            x2 = 0
        else:
            x2 = self.params['Арм.НомерФормы'][1] * 1000000

        if self.params['Арм.КлассЧисло'][1] > 0:
            if calc_diam == 10:
                a1 = 99
            else:
                a1 = 100 - calc_diam
            x3 = 100 * a1
        else:
            x3 = 0

        if like_pag:
            if self.params['Арм.КлассЧисло'][1] > 0:
                x4 = 100
            else:
                x4 = 0.1
        else:
            x4 = 1

        if like_pag or self.params['Рзм.ПеременнаяДлина'][1]:
            x5 = 0
        else:
            x5 = calc_length / 1000


        return (x1 + x2 + x3) * x4 + x5
    
    def get_param_ifc(self, par1, par2):
        """Возвращает par1 если выполнено семейством и par2 в др."""
        if self.params[self.if_ifc][1]:
            return self.params[par1][1]
        else:
            return self.params[par2][1]

    def set_param(self, par, val):
        self.params[par][0].Set(val)
            
    def get_param_value(self, parameter):
        if parameter.StorageType == StorageType.Integer:
            return parameter.AsInteger()
        if parameter.StorageType == StorageType.Double:
            if parameter.Definition.ParameterType == ParameterType.Number:
                return parameter.AsDouble()
            else:
                return round(to_mm(parameter.AsDouble())/self.round_n)*self.round_n
        if parameter.StorageType == StorageType.String:
            return parameter.AsString()
                
    def get_all_rebar_param(self):
        params = list(self.rebar.Parameters)
        params += doc.GetElement(self.rebar.GetTypeId()).Parameters
        for param in params:
            self.params.update({
                param.Definition.Name: (param, self.get_param_value(param))
                })

    def get_parameter_value(self, name):
        if name in self.params.keys():
            return self.params[name][1]
        else:
            return ''

    @classmethod
    def sort_key(cls, el):
        return el.sort_parameter

    @classmethod
    def remark(cls):
        params = [('sort_parameter', None, True)]
        res = cls.make_sort_list(cls.all_rebars, params)
        literas = set()
        for i in cls.all_rebars:
            literas.add(i.litera)
        litera_dicts = {}
        for i in literas:
            if i not in litera_dicts.keys():
                litera_dicts.update({i: 0})
        # echo(res)
        cls.scwithe_arr(res)
        for i in cls.sorted_elems:
            if not i[0].get_parameter_value('Рзм.ПогМетрыВкл'):
                add_elem = True
                litera_dicts[i[0].litera] += 1
                if not i[0].litera:
                    litera_dicts[i[0].litera] = cls.pass_numbers(litera_dicts[i[0].litera])
                for j in i:
                    if add_elem:
                        add_elem = False
                    j.set_param('Марка', str(litera_dicts[j.litera]))

        # echo(res)
        # cls.remark_action(res)

    @classmethod
    def scwithe_arr(cls, all):
        # new_arr = []
        if isinstance(all, dict):
            keys = list(all.keys())
            keys.sort(reverse=True)
            for key in keys:
                # echo(elem[0])
                cls.scwithe_arr(all[key])
        elif isinstance(all, list):
            cls.sorted_elems.append(all)

    @classmethod
    def pass_numbers(cls, numbs):
        curnam = numbs
        while curnam in cls._pass_numbers:
            curnam += 1
        return curnam


    @classmethod
    def make_sort_list(cls, elems, params=[]):
        if params:   
            params = copy.copy(params)
            param = params.pop()
            # echo(param[1])
            new_dict = {}
            for elem in elems:
                if param[0]:
                    par_val = getattr(elem, param[0])
                else:
                    par_val = elem.get_parameter_value(param[1])
                if par_val not in new_dict.keys():
                    new_dict.update({par_val: []})
                new_dict[par_val].append(elem)
            sec_dict = {}
            key_list = list(new_dict.keys())
            key_list.sort(reverse=param[2])
            for key in key_list:
                # echo(key)
                sec_dict.update({key:cls.make_sort_list(new_dict[key], params=params)})
            # echo('________')
            return sec_dict
        else:
            return elems

        # new_params = copy.copy(params)
        # if params: 
        #     curparams = new_params.pop(0)
        #     new_dict = {}
        #     for i in elems:
        #         if curparams[0]:
        #             cur_par = getattr(i, curparams[0])
        #         else:
        #             cur_par = i.get_parameter_value(curparams[1])
        #         if cur_par not in new_dict.keys():
        #             new_dict.update({cur_par: []})
        #         echo(cur_par)
        #         new_dict[cur_par].append(i)
        #     key_list = list(new_dict.keys())
        #     key_list.sort(reverse=curparams[2])
        #     sek_list = []
        #     for i in key_list:
        #         sek_list.append(cls.make_sort_list(new_dict[i], params=new_params))
        #     return sek_list
        # else:
        #     return elems

FORM.Start(2)

left_step = FORM.GetLines(1).add_textbox('Пропустить номера', '')
FORM.GetLines(1).add_label('Пропустить номера. Указать через запятую "1,2,5"')
left_step.Height=24
but_create = FORM.GetLines(2).add_button('Перемаркировать')
but_cancel = FORM.GetLines(2).add_button('Отмена')
FORM.calculate_size()

class execute_rebar_set(IExternalEventHandler):
    def Execute(self, app):
        # all_rebar = FilteredElementCollector(doc, curview.Id).OfClass(Rebar).ToElements()
        with Transaction(doc, 'Перемаркировать стержни') as t:
            t.Start()
            reb_rem = []
            res = [int(i) for i in left_step.GetValue().split(',') if i.isdigit()]
            Rebar_remark._pass_numbers = res
            for i in selection:
                reb_rem.append(Rebar_remark(i))
            Rebar_remark.remark()
            # Rebar_remark.compare(reb_rem)
            # __revit__.ActiveUIDocument.Selection.SetElementIds(Rebar_remark.selection)
            t.Commit()
        FORM.Close()

    def GetName(self):
        return 'New name'

def test():
    FORM.exEvent.Raise()
handler = execute_rebar_set()
exEvent = ExternalEvent.Create(handler)

but_cancel.AddFunction(FORM.Close)
but_create.AddFunction(test)
FORM.Create(exEvent)
