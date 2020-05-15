# coding: utf8
"""Добавляем необходимые фильтры для КЖ"""
# import os
import re
from Autodesk.Revit.UI import ExternalEvent, IExternalEventHandler
from common_scripts.get_elems.Get_revit_elements import Get_revit_elements as RB_FilteredElementCollector
# from math import pi

from Autodesk.Revit.DB import BuiltInCategory, Transaction, ViewSheet, FilteredElementCollector,\
Wall, BuiltInParameter, View, ViewSchedule, ElementId
# Transaction, ElementId, FilteredElementCollector, ParameterFilterElement, LogicalAndFilter, \
#                             LogicalOrFilter, ElementParameterFilter, ElementFilter, FilterRule, FilterStringRule, FilterInverseRule
# from Autodesk.Revit.DB.Structure import RebarInSystem, Rebar
# from System.Collections.Generic import List


uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
curview = uidoc.ActiveGraphicalView
selection = [doc.GetElement(elId) for elId in __revit__.ActiveUIDocument.Selection.GetElementIds()]

FORM.Start(2)
previous_kit = FORM.GetLines(1).add_textbox('Предыдущий комплект', '4.1.3')
FORM.GetLines(1).add_label('Предыдущий комплект в виде "4.1.1"')
previous_kit.Height=24

but_create = FORM.GetLines(2).add_button('Изменить комплект')
but_cancel = FORM.GetLines(2).add_button('Отмена')

FORM.calculate_size()

class Change_kit(IExternalEventHandler):
    """
    Изменяет комплект, марки, спецификации.
    """
    structure_elements = [
        BuiltInCategory.OST_Walls,
        BuiltInCategory.OST_StructuralFraming,
        BuiltInCategory.OST_StructuralColumns,
        BuiltInCategory.OST_Floors,
        BuiltInCategory.OST_StructuralFoundation,
        ]

    def Execute(self, app):
        # self.doc = app.ActiveUIDocument.Documentecho('Change_filters_in_schedule')
        self.previous_kit = previous_kit.GetValue()
        # self.previous_kit = '4.1.1'
        self.get_kit()
        with Transaction(doc, 'Меняем комплек') as t:
            t.Start()
            echo("{} меняем на  {}".format(self.previous_kit, self.kit))
            echo('Rename sheets')
            self.change_sheets_kit()
            echo('Rename structure_elements')
            self.change_elements_mark()
            echo('Rename views')
            self.change_view_names()
            echo('Change_filters_in_schedule')
            self.change_filters_in_schedule()
            echo('Change Мрк.МаркаКонструкции')
            self.change_mrk_mark_construction()
            t.Commit()
        FORM.Close()

    def get_kit(self):
        """Текущий комплект."""
        temp_temp = re.compile('(КЖ)[\d.]+')
        res = temp_temp.search(doc.Title)
        self.kit = res.group(0)[2:]

    @property
    def all_sheets(self):
        return FilteredElementCollector(doc).OfClass(ViewSheet).ToElements()

    def GetName(self):
        return 'Change kit'

    def change_sheets_kit(self):
        """Меняем комплект у листов."""
        templ = re.compile('КЖ' + self.previous_kit)
        for i in self.all_sheets:
            par = i.GetParameters('Орг.КомплектЧертежей')[0]
            res = None
            if par.AsString() and templ.search(par.AsString()):
                res = templ.search(par.AsString())
            if res:
                par.Set('КЖ' + self.kit)

    @property
    def all_structure_elements(self):
        elems = []
        for i in self.structure_elements:
            elems_cur = FilteredElementCollector(doc).OfCategory(i).ToElements()
            elems += [b for b in elems_cur if b.GetTypeId() != ElementId.InvalidElementId]
        return elems

    def change_elements_mark(self):
        templ = re.compile('-' + self.previous_kit + '-')
        for i in self.all_structure_elements:
            par = i.get_Parameter(BuiltInParameter.ALL_MODEL_MARK)
            if par and par.AsString() and templ.search(par.AsString()):
                par.Set(templ.sub('-'+self.kit+'-', par.AsString()))

    @property
    def all_views(self):
        return FilteredElementCollector(doc).OfClass(View).ToElements()

    def change_view_names(self):
        templ = re.compile('-'+self.previous_kit+'-')
        for i in self.all_views:
            par = i.get_Parameter(BuiltInParameter.VIEW_NAME)
            if par and par.AsString() and templ.search(par.AsString()):
                par.Set(templ.sub('-'+self.kit+'-', par.AsString()))
        templ = re.compile(self.previous_kit)
        for i in self.all_ViewSchedule:
            par = i.get_Parameter(BuiltInParameter.VIEW_NAME)
            if par and par.AsString() and templ.search(par.AsString()):
                par.Set(templ.sub(self.kit, par.AsString()))

    @property
    def all_ViewSchedule(self):
        return FilteredElementCollector(doc).OfClass(ViewSchedule).ToElements()

    def change_filters_in_schedule(self):
        aa = '-' + self.previous_kit + '-'
        templ = re.compile(aa)
        for i in self.all_ViewSchedule:
            definition = i.Definition
            k = 0
            for b in definition.GetFilters():
                if b.IsStringValue and templ.search(b.GetStringValue()):
                    new_val = templ.sub('-' + self.kit + '-', b.GetStringValue())
                    b.SetValue(new_val)
                    definition.SetFilter(k, b)
                k += 1

    def change_filters_names(self):
        templ = re.compile('-' + self.previous_kit + '-')
        for i in self.all_ViewSchedule:
            par = i.get_Parameter(BuiltInParameter.VIEW_NAME)
            if par and par.AsString() and templ.search(par.AsString()):
                par.Set(templ.sub('-'+self.kit+'-', par.AsString()))
                
    def change_mrk_mark_construction(self):
        cats = [
            BuiltInCategory.OST_Rebar,
            BuiltInCategory.OST_GenericModel
        ]
        elems = []
        templ = re.compile('-' + self.previous_kit + '-')
        for i in cats:
            elems_cur = FilteredElementCollector(doc).OfCategory(i)
            elems += [b for b in elems_cur if b.GetTypeId() != ElementId.InvalidElementId]
        elems_not_change = False
        for i in elems:
            elem_change = True
            if i.GroupId == ElementId.InvalidElementId:
                par = i.GetParameters('Мрк.МаркаКонструкции')
                if par:
                    par = par[0]
                    if not par.IsReadOnly:
                        if par.AsString() and templ.search(par.AsString()):
                            par.Set(templ.sub('-'+self.kit+'-', par.AsString()))
                            elem_change = False
            if elem_change:
                elems_not_change = True
        if elem_change:
            echo('Есть неизмененные элементы создайте вспомагательные спецификации для арматуры и обощенных моделей для проверки')
                            

def run():
    FORM.exEvent.Raise()

handler = Change_kit()
exEvent = ExternalEvent.Create(handler)

but_cancel.AddFunction(FORM.Close)
but_create.AddFunction(run)
FORM.Create(exEvent)