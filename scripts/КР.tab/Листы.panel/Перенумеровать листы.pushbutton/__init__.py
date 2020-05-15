from Autodesk.Revit.DB import *
from math import pi
import re

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
curview = uidoc.ActiveGraphicalView

symbol = ''

def by_last(sh):
    return sh.pattern.pop()

class RB_Sheet:
    all_sheet = []
    global_all_sheet = []
    max_len = 1
    names = []
    def __init__(self, sheet):
        self.sheet = sheet
        self.__class__.all_sheet.append(self)
        self.__class__.global_all_sheet.append(self)   
        self.pattern = []
        self.create_pattern(self.s_num)
        self.new_name = ""

    @property
    def s_num(self):
        return self.sheet.get_Parameter(BuiltInParameter.SHEET_NUMBER).AsString()
    #
    @property
    def name(self):
        return self.sheet.Name

    def change_name(self, name):
        symbols_count = self.__class__.names.count(name)
        cur_symb = symbol * symbols_count
        cur_name = name + cur_symb
        self.sheet.get_Parameter(BuiltInParameter.SHEET_NUMBER).Set(cur_name)
        self.__class__.names.append(name)

    def create_pattern(self, text):
        if text:
            match = re.search(r'^\D+', text)
            if match:
                self.pattern.append(match.group(0))
            else:
                match = re.search(r'^\d+', text)
                self.pattern.append(int(match.group(0)))
            self.create_pattern(text[len(match.group(0)):])
        else:
            pat_len = len(self.pattern)
            if pat_len > self.__class__.max_len:
                self.__class__.max_len = pat_len

    @classmethod
    def compare_all(cls):
        for sh in cls.all_sheet:
            need_to_add = cls.max_len - len(sh.pattern)
            sh.pattern = sh.pattern + ['' for i in range(need_to_add)]
        for i in range(cls.max_len):
             cls.all_sheet = sorted(cls.all_sheet, key = by_last)
        for i in cls.all_sheet:
            i.change_name(to_str(i.sheet.Id))
        iter = 0
        for i in cls.all_sheet:
            iter += 1
            i.new_name = to_str(iter)
    
    @classmethod
    def rename_all(cls):
        for i in cls.global_all_sheet:
            i.change_name(i.new_name)
    @classmethod
    def clear(cls):
        cls.all_sheet = []
        cls.max_len = 1
        cls.pattern = []

sheets = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Sheets).ToElements()
sets = {to_str(sheet.GetParameters('Орг.КомплектЧертежей')[0].AsString()) for sheet in sheets}

all_sheets_set = dict.fromkeys(sets, None)
for i in all_sheets_set.keys():
    all_sheets_set[i] = []

for sheet in sheets:
    el_name = to_str(sheet.GetParameters('Орг.КомплектЧертежей')[0].AsString())
    all_sheets_set[el_name].append(sheet)

with Transaction(doc, 'Перенумеровать листы') as t:
    t.Start()
    for sheets in all_sheets_set.values():
        for sheet in sheets:
            RB_Sheet(sheet)
        RB_Sheet.compare_all()
        RB_Sheet.clear()
    RB_Sheet.rename_all()
    t.Commit()