# coding: utf8
"""Формируем ВРС"""
import clr
import re
import copy
from Autodesk.Revit.DB import Transaction, SectionType, CellType
from System.Collections.Generic import List

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
selection = [doc.GetElement(elId) for elId in __revit__.ActiveUIDocument.Selection.GetElementIds()]
curview = uidoc.ActiveGraphicalView

class Format_VRS:
    tb = None
    names = ['','Марка конструкции', 'Напрягаемая арматура класса', 'Изделия арматурные', 'Изделия закладные', 'ВСЕГО']
    def __init__(self):
        cc = curview.Definition.GetFieldCount()
        for c in range(0, cc):
            curview.Definition.GetField(c).IsHidden = False
        self.tb = curview.GetTableData().GetSectionData(SectionType.Body)
        n_c = self.tb.NumberOfColumns
        n_r = self.tb.NumberOfRows

        for c in range(2, n_c):
            hide = True
            for r in range(0, n_r):
                if(self.tb.GetCellType(r,c) == CellType.ParameterText):
                    if not self.is_hide(self.tb.GetCellText(r,c)):
                        hide = False

            if hide or self.tb.GetCellText(0,c) not in self.names:
                curview.Definition.GetField(c).IsHidden = True


    def is_hide(self, val):
        if val == '0' or val == '':
            return True
        else:
            try:
                if val[:3] == '0,0':
                    return True
            except:
                return False


trans = Transaction(doc)
trans.Start("Сформировать ВРС")
form = Format_VRS()
trans.Commit()

# MEMORY.Close()
