# coding: utf8
"""Добавляем необходимые фильтры для КЖ"""
from math import pi

from Autodesk.Revit.DB.Structure import Rebar
from Autodesk.Revit.DB import FamilyInstance

doc = __revit__.ActiveUIDocument.Document

selection = [doc.GetElement(elId) for elId in __revit__.ActiveUIDocument.Selection.GetElementIds()]

rebar_resistance = {
    400: 355,
    500: 435 
}

concrete_resistance = {
    15: 7.5,
    20: 0.9,
    25: 1.05,
    30: 1.15,
    35: 1.3,
    40: 1.4,
    45: 1.5
}

def get_perep(ancer_base, diam, koef):
    if round(ancer_base * koef / diam) < ancer_base * koef / diam:
        return round(ancer_base * koef / diam + 1)
    else:
        return round(ancer_base / diam * koef)

if selection:
    if isinstance(selection[0], Rebar) or isinstance(selection[0], FamilyInstance):
        el = selection[0]
        el_type = doc.GetElement(el.GetTypeId())
        if (el_type.GetParameters('Рзм.Диаметр') and el_type.GetParameters('Арм.КлассБетона') and el_type.GetParameters('Арм.КлассЧисло')) or (el.GetParameters('Рзм.Диаметр') and el.GetParameters('Арм.КлассБетона') and el.GetParameters('Арм.КлассЧисло')):
            if el.GetParameters('Рзм.Диаметр'):
                diam = int(to_mm(el.GetParameters('Рзм.Диаметр')[0].AsDouble()))
            else:
                diam = int(to_mm(el_type.GetParameters('Рзм.Диаметр')[0].AsDouble()))
            if el.GetParameters('Арм.КлассБетона'):
                concrete = int(el.GetParameters('Арм.КлассБетона')[0].AsDouble())
            else:
                concrete = int(el_type.GetParameters('Арм.КлассБетона')[0].AsDouble())
            if el.GetParameters('Арм.КлассЧисло'):
                rebar_class = int(el.GetParameters('Арм.КлассЧисло')[0].AsDouble())
            else:
                rebar_class = int(el_type.GetParameters('Арм.КлассЧисло')[0].AsDouble())
            cur_con_res = concrete_resistance[concrete]
            cur_reb_res = rebar_resistance[rebar_class]

            ancer_base = (cur_reb_res * diam**2 * pi/4)/(cur_con_res * 2.5 * diam * pi)
            compress_anc = get_perep(ancer_base, diam, 0.75)*  diam
            bend_anc = get_perep(ancer_base, diam, 1)*  diam
            perep_bend = get_perep(ancer_base, diam, 1.2)*  diam
            perep_compr = get_perep(ancer_base, diam, 0.9)*  diam
            perep_sesm =  perep_bend * 1.3

            perep_comp_100 = get_perep(ancer_base, diam, 1.4)*  diam
            perep_comp_100_sesm = round(get_perep(ancer_base, diam, 1.4) * 1.3) *  diam
            perep_bend_100 = get_perep(ancer_base, diam, 2)*  diam
            perep_bend_100_sesm = round(get_perep(ancer_base, diam, 2) * 1.3) *  diam

            message(
                """
                Диаметр Ø {} Бетон B{} Арматура А{}\n\r
                Длина анк(сжатых стержней), {} мм
                Длина анк(растянутых стержней), {} мм
                Длина переп(растянутые стержни), {} мм
                Длина переп(сжатые стержни), {} мм
                Длина переп(сейсмика), {} мм
                Длина переп 100% одно сеч. с отгибами (раст), {} мм
                Длина переп 100% одно сеч. с прямыми (раст), {} мм
                Длина переп 100% одно сеч. с отгибами (раст) сей, {} мм
                Длина переп 100% одно сеч. с прямыми (раст) сей, {} мм

                """.format(
                diam,
                concrete,
                rebar_class,
                compress_anc,
                bend_anc,
                perep_bend,
                perep_compr,
                perep_sesm,
                perep_comp_100,
                perep_comp_100_sesm,
                perep_bend_100,
                perep_bend_100_sesm))
        else:
            message("Нет параметра или Арм.КлассЧисло или Арм.КлассБетона или Рзм.Диаметр")