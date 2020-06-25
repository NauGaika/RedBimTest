# -*- coding: utf-8 -*-
from common_scripts import echo
# Console         : есть консоль
# Loop            : есть петлевой выступ
# Teeth           : есть зуб
# TeethPart       : зуб на частичную длину (например, по всей длине внутреннего слоя, если длина слоя меньше общей длины изделия)
# TeethCut        : зуб с подрезкой (вырезом) части зуба.
# EndLeft         : если смотреть на изделие с внутренней стороны, то наружный слой "загибается" с левой стороны
# EndRight        : если смотреть на изделие с внутренней стороны, то наружный слой "загибается" с правой стороны
# Heat            : наличие утеплителя (поскольку возможны варианты внутренних стен, лучше бы указать)
# Window          : наличие проема под окно
# Balkony         : наличие проема под балконную дверь
# Door            : наличие проема под входную дверь
# TechCut         : наличие технологических проемов в количестве больше 3 штук
# StapleLeft120   : скобы монтажные слева, выступающие на 120 мм
# StapleRight120  : то же, справа
# StapleLeft150   : скобы монтажные слева, выступающие на 150 мм
# StapleRight150  : то же, справа
# StapleLeft245   : скобы монтажные слева, выступающие на 245 мм
# StapleRight245  : то же, справа
# StapleLeft275   : скобы монтажные слева, выступающие на 275 мм
# StapleRight275  : то же, справа
# StapleTop       : скобы монтажные по верху изделия
#  RDS             : размеры РДС "вживую"
# RDSLight        : размеры РДС в свету

class Precast_panel_indastry(object):
    def add_indastry_parameter(self):
        """
        Добавление параметров для ПИ.

        Парамтеры формируются в виде строки и записываются в панель.
        Остальные параметры уже записаны в панели через формцлы revit
        Так же записывается значение BDS_Balcony, если окно - балкон
        и BDS_Window, если окно - окно
        т.к. дверей нет - записываем, что это равно 0.

        В зависимости от Тип окна (параметр семейства)
        заполняем тип окна window_type
        центр
        угол правый
        угол левый
        угол правый загиб
        угол левый загиб
        
        если тип окна = 0 - это рядовое окно и не важно с какой оно стороны
        если окно справа - базис Y совпадает с FacingOrientation - это правое окно
        иначе - левое

        """
        parameters = {}
        parameters["Console"] = False
        parameters["Loop"] = False
        parameters["Teeth"] = False
        parameters["TeethPart"] = False
        parameters["TeethCut"] = False
        parameters["EndLeft"] = self["BDS_LeftEndType"] == 1
        parameters["EndRight"] = self["BDS_RightEndType"] == 1
        parameters["Heat"] = True
        windows_count = 0
        balcony_count = 0
        p = 0
        for window in self.windows:
            p += 1
            if window.window_type == "Balcony":
                balcony_count += 1
                window["BDS_Balkony"] = 1
            else:
                window["BDS_Balkony"] = 0
            if window.window_type == "Window":
                windows_count += 1
                window["BDS_Window"] = 1
            else:
                window["BDS_Window"] = 0
            window["BDS_Door"] = 0
            parameters["RDSLightHeight_" + str(p)] = window["BDS_RDSLightHeight"]
            parameters["BDS_RDSLightLength_" + str(p)] = window["BDS_RDSLightLength"]

            element = window.element
            if window["Тип окна"] is not None:
                if window["Тип окна"] == 0:
                    window_type = "центр"
                else:
                    window_type = "угол"
                    if element.GetTransform().BasisY.Z > 0 or element.GetTransform().BasisY.IsAlmostEqualTo(element.FacingOrientation):
                        window_type += " правый"
                    else:
                        window_type += " левый"
                    if window["Тип окна"] == 1:
                        window_type += " загиб"
                window["BDS_PositionType"] = window_type
            else:
                echo("{} Не обновлено либо не имеет параметр Тип окна".format(window))

        parameters["Window"] = windows_count
        parameters["Balkony"] = balcony_count
        parameters["Door"] = False
        parameters["TechCut"] = False
        parameters["StapleLeft120"] = False
        parameters["StapleRight120"] = False
        parameters["StapleLeft150"] = False
        parameters["StapleLeft245"] = False
        parameters["StapleRight245"] = False
        parameters["StapleLeft275"] = False
        parameters["StapleRight275"] = False
        parameters["StapleTop"] = False
        self.industry_parameter = parameters

    @property
    def industry_parameter(self):
        if not hasattr(self, "_industry_parameter"):
            self._industry_parameter = {}
        return self._industry_parameter

    @industry_parameter.setter
    def industry_parameter(self, val):
        "Установить значение параметра в виде строки."
        self._industry_parameter = val
        res = []
        for key in sorted(val.keys()):
            value = val[key]
            if value:
                res.append("{}:{}".format(key, value))
        self["BDS_Modifying"] = "|".join(res)
