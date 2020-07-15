# -*- coding: utf-8 -*-
from ..Common import Precast_component


class Precast_unit_member(Precast_component):
    "Составные части узла."

    def __init__(self, unit_member, parent=None, doc=None, analys_geometry=False):
        super(Precast_unit_member, self).__init__(unit_member, doc, analys_geometry=analys_geometry, parent=parent)

    def __repr__(self):
        return "Составная часть узла id {} с именем {}".format(self.element.Id.IntegerValue, self.element.Symbol.Family.Name)
