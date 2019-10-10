# coding: utf8
from Autodesk.Revit.DB import SectionType, TableMergedCell, TableCellStyle, TableCellStyleOverrideOptions, ElementId
from common_scripts import echo, to_feet, to_str

class RB_Scheduled:
    """Работа со спецификамиями."""

    def __init__(self, doc):
        """Инициализируем спецификацию."""
        self.doc = doc
        self.sched = self.doc.ActiveView
        self.td = self.sched.GetTableData()
        self.head = self.td.GetSectionData(SectionType.Header)
        self.body = self.td.GetSectionData(SectionType.Body)

    @property
    def row_height(self):
        return self.__row_height

    def set_row_height(self, val, row_num = -1):
        self.__row_height = float(val)
        if row_num < 0:
            for i in range(0, self.head.NumberOfRows):
                self.head.SetRowHeight(i, to_feet(val))
        else:
            self.head.SetRowHeight(row_num, to_feet(val))

    def set_row_val(self, w, h, val):
        self.head.SetCellText(h, w, to_str(val))

    def set_row_list(self, r, arr):
        for i in range(0, len(arr)):
            self.head.SetCellText(r, i, to_str(arr[i]))

    def set_column_count(self, count):
        for i in range(0, count - 1):
            self.head.InsertColumn(1)

    def add_rows(self, pos, count=1):
        for i in range(0, count-1):
            self.head.InsertRow(1)

    def set_row_width(self, arr):
        for i in range(0, len(arr)):
            self.head.SetColumnWidth(i, to_feet(arr[i]))
    def merge_cell(self, top, left, bottom, right):
        tmc = TableMergedCell(top, left, bottom, right)
        self.head.SetMergedCell(top, left, tmc)

    def remove_all_row_and_column(self):
        """Удаляет все строки и столбцы из заголовка, кроме одного."""
        for i in range(1, self.head.NumberOfColumns):
            self.head.RemoveColumn(self.head.LastColumnNumber)
        for i in range(1, self.head.NumberOfRows):
            self.head.RemoveRow(self.head.LastRowNumber)
