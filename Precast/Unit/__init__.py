# -*- coding: utf-8 -*-
# from common_scripts import echo
# from Autodesk.Revit.DB import Transaction
from ..Common import Precast_component
from ..Unit_member import Precast_unit_member


class Precast_unit(Precast_component):
    "Узлы."
    all_units = {}
    def __init__(self, unit, doc=None, analys_geometry=False):
        super(Precast_unit, self).__init__(unit, doc, analys_geometry=analys_geometry)
        self.panels = set()
        self._subcomponents = None

    def __repr__(self):
        return "Узел id {} с именем {}".format(self.element.Id.IntegerValue, self.element.Symbol.Family.Name)

    @classmethod
    def create(cls, unit, doc, panel):
        u_id = unit.Id
        if u_id not in cls.all_units.keys():
            ob = cls(unit, doc=doc)
            cls.all_units[u_id] = ob
        cls.all_units[u_id].panels.add(panel)
        return cls.all_units[u_id]
        
    def get_subcomponents(self, elem_id, all_elems=None):
        "Рекурсивно получить все составляющие узлов."
        primary = False
        if all_elems is None:
            all_elems = []
            primary = True
        elem = self.doc.GetElement(elem_id)
        all_elems.append(elem)
        for i in elem.GetSubComponentIds():
            self.get_subcomponents(i, all_elems=all_elems)
        if primary:
            return all_elems

    @property
    def subcomponents(self):
        "Составляющие узлов."
        if self._subcomponents is None:
            self._subcomponents = self.get_subcomponents(self.element.Id)
            self._subcomponents = [Precast_unit_member(i, doc=self.doc, parent=self) for i in self._subcomponents]
        return self._subcomponents
