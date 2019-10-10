# -*- coding: utf-8 -*-
import clr
from Autodesk.Revit.DB import BuiltInCategory, FilteredElementCollector, BuiltInParameter
from Autodesk.Revit.DB.Structure import RebarBarType, RebarShape
from Autodesk.Revit.UI.Selection import ObjectType, ISelectionFilter
from common_scripts import *
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

def get_RebarBarType(diam, mark, is_pag):
    rebars = FilteredElementCollector(doc).OfClass(RebarBarType).ToElements()
    for rebar in rebars:
        if to_mm(rebar.GetParameters('Рзм.Диаметр')[0].AsDouble()) == diam:
            if rebar.GetParameters('Арм.КлассЧисло')[0].AsDouble() == mark:
                if rebar.GetParameters('Рзм.ПогМетрыВкл')[0].AsInteger() == is_pag:
                    return rebar
def get_RebarShape(name):
    rebars = FilteredElementCollector(doc).OfClass(RebarShape).ToElements()
    for rebar in rebars:
        if name == rebar.get_Parameter(BuiltInParameter.SYMBOL_NAME_PARAM).AsString():
            return rebar

def _get_protect_layer(elem, bip):
    el_id = elem.get_Parameter(bip)
    if el_id:
        el_id = el_id.AsElementId()
        return doc.GetElement(el_id).CoverDistance

def get_protect_layer(elem):
    """Получаем значения защитных слоев."""
    res = {
        'top': _get_protect_layer(elem, BuiltInParameter.CLEAR_COVER_TOP),
        'other': _get_protect_layer(elem, BuiltInParameter.CLEAR_COVER_OTHER),
        'bottom': _get_protect_layer(elem, BuiltInParameter.CLEAR_COVER_BOTTOM),
        'int': _get_protect_layer(elem, BuiltInParameter.CLEAR_COVER_INTERIOR),
        'ext': _get_protect_layer(elem, BuiltInParameter.CLEAR_COVER_EXTERIOR)
    }
    return res
