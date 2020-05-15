import re
from System.Collections.Generic import List
from math import pi, ceil
from Autodesk.Revit.DB import BuiltInCategory, BuiltInParameter, Transaction, FilteredElementCollector, ViewSheet, ElementId, RevitLinkInstance, ProjectLocation, Line, ElementTransformUtils,XYZ
from Autodesk.Revit.UI import ExternalEvent, IExternalEventHandler

from Autodesk.Revit.DB.Structure import Rebar, RebarHookOrientation, RebarHookType, RebarStyle
from common_scripts.get_elems.RB_selections import RB_selections

from Autodesk.Revit.UI.Selection import ObjectType
from Autodesk.Revit.Exceptions import OperationCanceledException
from common_scripts.RB_Scripts.RB_Rebar import RB_Rebar


doc = __revit__.ActiveUIDocument.Document

selection = [doc.GetElement(elId) for elId
             in __revit__.ActiveUIDocument.Selection.GetElementIds()]

FORM.Start(3)

left_step = FORM.GetLines(1).add_textbox('Шаг учащения слева', '50')
FORM.GetLines(1).add_label('Шаг учащения слева')
left_step.Height=24

left_count = FORM.GetLines(1).add_textbox('Количество стержней учащения слева', '5')
FORM.GetLines(1).add_label('Количество стержней учащения слева')
left_count.Height=24

left_increase = FORM.GetLines(1).add_checked_list_box('Учащение слева', [('Да', True)])
FORM.GetLines(1).add_label('Добавить учащение слева')
left_increase.Height=24

right_step = FORM.GetLines(2).add_textbox('Шаг учащения справа', '50')
FORM.GetLines(2).add_label('Шаг учащения справа')
right_step.Height=24

right_count = FORM.GetLines(2).add_textbox('Количество стержней учащения справа', '5')
FORM.GetLines(2).add_label('Количество стержней учащения справа')
right_count.Height=24

right_increase = FORM.GetLines(2).add_checked_list_box('Учащение справа', [('Да', True)])
FORM.GetLines(2).add_label('Добавить учащение справа')
right_increase.Height=24

but_create = FORM.GetLines(3).add_button('Разделить')
but_cancel = FORM.GetLines(3).add_button('Отмена')

FORM.calculate_size()

class execute_rebar_set(IExternalEventHandler):
    def Execute(self, app):
        t = Transaction(doc, 'Добавить учащение')
        t.Start()
        start_rebar = RB_Rebar(selection[0])
        start_rebar_count = int(left_count.GetValue())
        end_rebar_count = int(right_count.GetValue())
        start_step = to_feet(int(left_step.GetValue()))
        end_step = to_feet(int(right_step.GetValue()))
        path_length =  start_rebar.ArrayLength
        normale = 	start_rebar.Normal
        start_space = start_rebar.rebar.MaxSpacing
        start_rebar_count
        translate_vector = normale
        start_rebar_left = True
        start_rebar_right = True
        left_space = 0
        right_space = 0
        rebars = List[ElementId]()
        if left_increase.GetValue()['Да']:
            left_space = (start_rebar_count-1)*start_step
            left_rebar = start_rebar.copy_by_normal_length(XYZ(0, 0, 0))
            left_rebar.SetAsNumberWithSpacing(start_rebar_count, start_step)
            rebars.Add(left_rebar.rebar.Id)
        if right_increase.GetValue()['Да']:
            right_space = (end_rebar_count-1)*end_step
            right_rebar = start_rebar.copy_by_normal_length(normale*(path_length-right_space))
            right_rebar.SetAsNumberWithSpacing(end_rebar_count, end_step)
            rebars.Add(right_rebar.rebar.Id)

        if left_increase.GetValue()['Да'] or right_increase.GetValue()['Да']:
            biv = path_length - right_space - left_space
            reb_count = ceil(biv / start_space)
            biv = biv - (reb_count-1) * start_space
            if left_increase.GetValue()['Да'] and right_increase.GetValue()['Да']:
                biv = biv/2
            if not left_increase.GetValue()['Да']:
                biv = 0
            # echo(to_mm(biv))
            rebars.Add(start_rebar.rebar.Id)
            __revit__.ActiveUIDocument.Selection.SetElementIds(rebars)
            start_rebar.translate(normale*(left_space + biv))
            start_rebar.SetAsNumberWithSpacing(reb_count, start_space, first=True, last=True)

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
