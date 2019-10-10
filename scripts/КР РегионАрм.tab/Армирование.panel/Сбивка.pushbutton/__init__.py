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

start_increase = FORM.GetLines(1).add_checked_list_box('Учащение слева', [('Да', True)])
FORM.GetLines(1).add_label('Сбивка начало')
start_increase.Height=24
end_increase = FORM.GetLines(2).add_checked_list_box('Учащение справа', [('Да', True)])
FORM.GetLines(2).add_label('Сбивка конец')
end_increase.Height=24

but_create = FORM.GetLines(3).add_button('Добавить')
but_cancel = FORM.GetLines(3).add_button('Отмена')

FORM.calculate_size()

class execute_rebar_set(IExternalEventHandler):
    def Execute(self, app):
        if start_increase.GetValue()['Да'] or end_increase.GetValue()['Да']:
            t = Transaction(doc, 'Добавить учащение')
            t.Start()
            rebar = RB_Rebar(selection[0])
            path_length =  rebar.ArrayLength
            normale = 	rebar.Normal
            start_space = rebar.rebar.MaxSpacing
            reb_count = int(ceil(path_length / start_space))
            biv = (path_length - (reb_count-1) * start_space)
            rebars = List[ElementId]()
            rebars.Add(rebar.rebar.Id)
            if end_increase.GetValue()['Да'] and start_increase.GetValue()['Да']:
                biv = biv / 2
            if biv > to_feet(20):
                rebar.SetAsNumberWithSpacing(reb_count, start_space)
                if start_increase.GetValue()['Да']:
                    rebar.translate(normale*biv)
                    tr = rebar.copy_by_normal_length(normale * -biv)
                    tr.SetAsSingle()
                    rebars.Add(tr.rebar.Id)
                if end_increase.GetValue()['Да']:
                    tr = rebar.copy_by_normal_length(normale * (start_space * (reb_count-1) + biv))
                    tr.SetAsSingle()
                    rebars.Add(tr.rebar.Id)
                __revit__.ActiveUIDocument.Selection.SetElementIds(rebars)
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
