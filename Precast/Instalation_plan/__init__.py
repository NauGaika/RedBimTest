# -*- coding: utf-8 -*-
import json
import io
import os
import sys
from Autodesk.Revit.DB import FilteredElementCollector, Grid, IntersectionResultArray
from Autodesk.Revit.DB import RevitLinkInstance, BuiltInCategory, FamilyInstance, Wall
from Autodesk.Revit.DB import FilteredElementCollector, Level, Transaction
from Autodesk.Revit.DB import WorksetConfigurationOption, WorksetConfiguration, OpenOptions, ElementId, ModelPathUtils
from Autodesk.Revit.DB import RelinquishOptions, TransactWithCentralOptions, SynchronizeWithCentralOptions
from Autodesk.Revit.UI import FileOpenDialog
from clr import StrongBox
from math import pi
from common_scripts import echo, message
from common_scripts.line_print import Line_printer
from System.Windows.Forms import FolderBrowserDialog, DialogResult
from .Instalation_plan_json import Instalation_plan_json
from .Instalation_plan_link import Instalation_plan_link
from .Instalation_plan_tests import Instalation_plan_tests


class Instalation_plan(Instalation_plan_tests, Instalation_plan_json):
    def __init__(self, doc):
        self.doc = doc
        super(Instalation_plan, self).__init__()

    def create_instalation_plan(self):
        "Создание файлов монтажного плана."
        self.path_to_save = self.select_path()
        self.start_point, self.start_grids = self.find_start_point_and_grids()
        self.recalculate_grid_origins(
            self.grids, self.start_point, self.start_grids)
        Instalation_plan_link.create(self.rvt_links, self.start_point)
        global_obj = Instalation_plan_link.find_panels_in_links(to_old=True)
        old_format_obj = Instalation_plan_link.all_panel_dict_old(global_obj)
        res = {
            "levels": old_format_obj,
            "axes": self.grids_to_dict(self.grids, elevation=False)
        }
        self.save_montain_plan_to_file(res)
        message("Монтажный план выгружен в {}".format(self.path_to_save))

    def create_grid_plan(self):
        self.path_to_save = self.select_path()
        self.start_point, self.start_grids = self.find_start_point_and_grids()
        self.recalculate_grid_origins(
            self.grids, self.start_point, self.start_grids)
        self.save_grids_file(self.grids_to_dict(self.global_grids))
        message("Файл осей план выгружен в {}".format(self.path_to_save))

    def get_coloristic_mark(self):
        "Получаем колористические марки."
        obj_from_file = self.open_coloristic_file()
        coloristic_obj = self.get_all_panels_from_dict(obj_from_file)
        self.start_point, self.start_grids = self.find_start_point_and_grids()
        Instalation_plan_link.create(self.rvt_links, self.start_point)
        global_obj = Instalation_plan_link.find_panels_in_links()
        res_obj = self.get_coloristic_tag_for_panels(
            global_obj, coloristic_obj)
        self.set_coloristic_tag(res_obj)

    def select_path(self):
        "Выбираем путь куда сложим монтажный план и файл осей."
        dir_path = FolderBrowserDialog()
        res = dir_path.ShowDialog()
        if res == DialogResult.OK and dir_path.SelectedPath:
            dir_path = dir_path.SelectedPath
        return dir_path

    def find_start_point_and_grids(self):
        "Находит стартовую точку осей и ось."
        all_lines = [i["line"] for i in self.grids.values()]
        [i.MakeUnbound() for i in all_lines]
        min_x = float("inf")
        min_y = float("inf")
        min_point = None
        axis = [None, None]
        for i in all_lines:
            for j in all_lines:
                itersect_result = StrongBox[IntersectionResultArray]()
                i.Intersect(j, itersect_result)
                if itersect_result.Value:
                    point = itersect_result.Value[0].XYZPoint
                    if round(point.X, 5) < min_x or round(point.Y, 5) < min_y:
                        min_x = round(point.X, 5)
                        min_y = round(point.Y, 5)
                        min_point = point
                        axis = [i, j]
        return min_point, axis

    @property
    def grids(self):
        if not hasattr(self, "_grids"):
            self._grids = FilteredElementCollector(self.doc).OfClass(
                Grid).WhereElementIsNotElementType().ToElements()
            self._grids = {
                i.Name: {
                    "name": i.Name,
                    "direction": i.Curve.Direction,
                    "line": i.Curve,
                    "el": i,
                    "global": i.LookupParameter("BDS_AxisGlobal").AsString() if i.LookupParameter("BDS_AxisGlobal") else ""
                } for i in self._grids}
            # echo(self._grids)
        return self._grids

    @property
    def global_grids(self):
        if not hasattr(self, "_global_grids"):
            self._global_grids = {key: i for key,
                                  i in self.grids.items() if i["global"]}
        return self._global_grids

    @property
    def levels(self):
        if not hasattr(self, "_levels"):
            self._levels = FilteredElementCollector(self.doc).OfClass(
                Level).WhereElementIsNotElementType().ToElements()
            self._levels = [{
                "Name": i.Name,
                "Elevation": round(i.Elevation * 304.8)
            } for i in self._levels if i.Name.isdigit()]
            # echo(self._levels)
            self._levels.sort(key=lambda x: x["Name"])
        return self._levels

    @property
    def rvt_links(self):
        if not hasattr(self, "_rvt_links"):
            self._rvt_links = FilteredElementCollector(self.doc).OfClass(
                RevitLinkInstance).WhereElementIsNotElementType().ToElements()
        return self._rvt_links

    @property
    def rvt_docs(self):
        if not hasattr(self, "_rvt_docs"):
            self._rvt_docs = {}
            for i in self.rvt_links:
                if i.GetLinkDocument() not in self._rvt_docs.keys():
                    self._rvt_docs.setdefault(
                        i.GetLinkDocument(), self.doc.GetElement(i.GetTypeId()))
        return self._rvt_docs

    def recalculate_grid_origins(self, grids, start_point, start_grids):
        for key, i in grids.items():
            orto_start_line = start_grids[1] if i["direction"].IsAlmostEqualTo(
                start_grids[0].Direction) or i["direction"].IsAlmostEqualTo(start_grids[0].Direction.Negate()) else start_grids[0]
            i["line"].MakeUnbound()
            line = i["line"]
            itersect_result = StrongBox[IntersectionResultArray]()
            line.Intersect(orto_start_line, itersect_result)
            i["origin"] = itersect_result.Value[0].XYZPoint - start_point

    def save_grids_file(self, save_obj):
        file_name = r"Файл сеток.json"
        with io.open(os.path.join(self.path_to_save, file_name), "w", encoding='utf8') as f:
            el = json.dumps(save_obj, sort_keys=True,
                            indent=4, ensure_ascii=False)
            el = el.replace('"global"', '"GlobalName"')
            el = el.replace('"local"', '"LocalName"')
            el = el.replace('"position"', '"Origin"')
            el = el.replace('"rotation"', '"Direction"')
            f.write(el)
            f.close()

    def save_montain_plan_to_file(self, save_obj):
        file_name = r"mp-1.json"
        with io.open(os.path.join(self.path_to_save, file_name), "w", encoding='utf8') as f:
            json.dump(save_obj, f, sort_keys=True,
                      indent=4, ensure_ascii=False)
            f.close()

    def open_coloristic_file(self):
        dialog = FileOpenDialog("Файл колористики json|*.json")
        dialog.Show()
        mpath = dialog.GetSelectedModelPath()
        path = ModelPathUtils.ConvertModelPathToUserVisiblePath(mpath)
        with io.open(path, "r", encoding='utf8') as f:
            text = f.read()
            text = text.replace('"rotate"', '"rotation"')
            return json.loads(text)

    def get_coloristic_tag_for_panels(self, global_obj, coloristic_obj):
        echo("Сравнение по повороту отключено")
        echo("Сравнение по марке отключено")
        result_obj = {}
        for section_num in coloristic_obj.keys():
            if section_num in global_obj.keys():
                for level_num in coloristic_obj[section_num].keys():
                    if level_num in global_obj[section_num]:
                        for c_panel in coloristic_obj[section_num][level_num]:
                            comp = False
                            for r_panel in global_obj[section_num][level_num]:
                                if self.compare_position(c_panel, r_panel):
                                    if comp:
                                        echo("Найдено две панели по одной позиции")
                                    comp = True
                                    result_obj.setdefault(
                                        r_panel["panel"].document, {})
                                    result_obj[r_panel["panel"].document].setdefault(
                                        r_panel["panel"], {})
                                    result_obj[r_panel["panel"].document][r_panel["panel"]][level_num] = c_panel["colorIndex"]
                                    # echo("Найдена панель {} с маркой {} в секции {} на этаже {}".format(c_panel["mark"], r_panel["mark"], section_num, level_num))
                                    break
                            else:
                                echo("Не найдена панель {} в секции {} на этаже {}".format(c_panel["mark"], section_num, level_num))
                    else:
                        echo("Не найден {} этаж секции {} в текущем файле".format(
                            level_num, section_num))
            else:
                echo("Не найдена секция {} в текущем файле".format(section_num))
        return result_obj

    def compare_position(self, element_1, element_2, tollerance=100):
        """
        Сравнение панелей по позициям.

        Если позиции по X, Y и Z совпадают в пределах tollerance.
        Они равны.

        Сейчас отключена проверка по повороту и марке.
        """
        # mark = element_1["mark"] == element_2["mark"]
        # if mark:
        # return True
        p1 = element_1["position"]
        p2 = element_2["position"]
        position = (abs(p1["X"] - p2["X"]) <= tollerance) and (
            abs(p1["Y"] - p2["Y"]) <= tollerance) and (abs(p1["Z"] - p2["Z"]) <= tollerance)
        # rotation = round(element_1["rotation"], 3) == round(element_2["rotation"], 3)
        rotation = True
        if rotation and position:
            return True

    def set_coloristic_tag(self, obj):
        """
        Устанавливает коллористические марки.

        Открывает файл с закрытыми рабочими наборами.
        Для этого создается конфиг open_opt

        Проходим по всем документам и панелям, которые переданы в obj
        Выгружаем связь.
        Открываем документ.
        Проверяем можно ли вносить изменения в документ.
        Пробуем внести изменения.
        Проходим по всем панелям и уровням.
        Получаем в документе связи панель по ID.
        Проходим по всем уровням. 
        Для каждой колористик Tag устанавливаем марку по уровню.
        Если файл общий. Синхронизироваться.
        Если файл не общий - просто сохранить.
        В противном случае закрыть документ
        """
        workset_config_option = WorksetConfigurationOption.CloseAllWorksets
        workset_config = WorksetConfiguration(workset_config_option)
        open_opt = OpenOptions()
        open_opt.SetOpenWorksetsConfiguration(workset_config)
        app = self.doc.Application
        for doc, panels in obj.items():
            title = doc.Title
            m_p = ModelPathUtils.ConvertUserVisiblePathToModelPath(
                doc.PathName)
            rvt_type = self.rvt_docs[doc]
            rvt_type.Unload(None)
            cur_doc = app.OpenDocumentFile(m_p, open_opt)
            if not cur_doc.IsReadOnly:
                try:
                    with Transaction(cur_doc, "Вносим изменения") as t:
                        t.Start()
                        for panel, levels in panels.items():
                            panel = cur_doc.GetElement(ElementId(panel.Id))
                            for level, mark in levels.items():
                                level = level if len(level) > 1 else "0" + level
                                panel.LookupParameter(
                                    "BDS_ColoristicsTag_Floor" + level).Set(mark)
                        t.Commit()
                    if cur_doc.IsWorkshared:
                        twc_opts = TransactWithCentralOptions()
                        swc_opts = SynchronizeWithCentralOptions()
                        swc_opts.SetRelinquishOptions(RelinquishOptions(True))
                        swc_opts.Comment = "Атоматическая синхронизация КЖС"
                        cur_doc.SynchronizeWithCentral(twc_opts, swc_opts)
                    cur_doc.Close(True)
                except:
                    echo(sys.exc_info()[1])
                    cur_doc.Close(False)
            else:
                echo("Файл {} доступен только для чтения".format(title))
                cur_doc.Close(False)
            rvt_type.Load()
            echo("Обработали связь {}".format(title))