# coding: utf8
from Autodesk.Revit.DB import SectionType, TableMergedCell, TableCellStyle, TableCellStyleOverrideOptions, ElementId
from common_scripts import echo, to_feet, to_str

class RB_Scheduled:
    """Работа со спецификамиями."""

    def __init__(self, view):
        """Инициализируем спецификацию."""
        self.sched = view
        self.td = self.sched.GetTableData()
        self.head = self.td.GetSectionData(SectionType.Header)
        self.body = self.td.GetSectionData(SectionType.Body)

    @property
    def row_height(self):
        if not hasattr(self, "__row_height"):
            self.__row_height = float(6) / 304.8
        return self.__row_height

    @row_height.setter
    def row_height(self, val):
        self.__row_height = val  

    def set_row_height(self, val=None, row_num = -1):
        if val is not None:
            self.row_height = val / 304.8
        # echo(self.row_height)
        if row_num < 0:
            for i in range(0, self.head.NumberOfRows):
                self.head.SetRowHeight(i, self.row_height)
        else:
            self.head.SetRowHeight(row_num, self.row_height)

    def set_row_val(self, w, h, val, pref="-", rounded=None):
        if val:
            if rounded is not None:
                if rounded < 1:
                    val = int(val)
                else:
                    val = round(val, rounded)
            else:
                val = val
        else:
            val = pref
        self.head.SetCellText(h, w, to_str(val))

    def set_row_list(self, r, arr):
        for i in range(0, len(arr)):
            self.head.SetCellText(r, i, to_str(arr[i]))

    def set_column_count(self, count):
        for i in range(0, count - 1):
            self.head.InsertColumn(1)

    def add_rows(self, pos, count=1):
        for i in range(0, count-1):
            self.set_row_height(row_num=0)
            self.head.InsertRow(0)

    def set_table_width(self, width):
        self.body.SetColumnWidth(0, to_feet(width))

    def set_columns_width(self, arr, start=0):
        for i in range(0 + start, len(arr) + start):
            self.head.SetColumnWidth(i, to_feet(arr[i]))

    def merge_cell(self, left, top, right, bottom):
        tmc = TableMergedCell(top, left, bottom, right)
        self.head.MergeCells(tmc)

    def remove_all_row_and_column(self):
        """Удаляет все строки и столбцы из заголовка, кроме одного."""
        for i in range(1, self.head.NumberOfColumns):
            self.head.RemoveColumn(self.head.FirstColumnNumber)
        for i in range(1, self.head.NumberOfRows):
            self.head.RemoveRow(self.head.FirstRowNumber)
        self.head.ClearCell(0,0)

    def set_cell_border(self, row, column, left, top, right, bottom):
        "Скрывает или показывает границы ячейки"
        tcs = self.head.GetTableCellStyle(row, column)
        csoo = tcs.GetCellStyleOverrideOptions()
        if not left:
            csoo.BorderLeftLineStyle = True
            tcs.BorderLeftLineStyle = ElementId.InvalidElementId
        if not top:
            csoo.BorderTopLineStyle = True
            tcs.BorderTopLineStyle = ElementId.InvalidElementId
        if not bottom:
            csoo.BorderBottomLineStyle = True
            tcs.BorderBottomLineStyle = ElementId.InvalidElementId
        if not right:
            csoo.BorderRightLineStyle = True
            tcs.BorderRightLineStyle = ElementId.InvalidElementId
        tcs.SetCellStyleOverrideOptions(csoo)
        
        self.head.SetCellStyle(row, column, tcs)

    def set_cell_font_size(self, row, column, font_size):
        tcs = self.head.GetTableCellStyle(row, column)
        csoo = tcs.GetCellStyleOverrideOptions()
        # echo(tcs.TextSize)
        tcs.TextSize = font_size * 3.779527559055
        csoo.FontSize = True
        tcs.SetCellStyleOverrideOptions(csoo)
        self.head.SetCellStyle(row, column, tcs)

