# -*- coding: utf-8 -*-
import re
import os
from math import pi
from datetime import datetime
from common_scripts import echo
from System.Collections.Generic import List

from Autodesk.Revit.DB import BuiltInCategory, BuiltInParameter, Transaction, FilteredElementCollector, ElementId, Category
from Autodesk.Revit.DB import ElementTransformUtils, Transform, CopyPasteOptions, CategorySet, InstanceBinding, SharedParameterElement
from Autodesk.Revit.DB import IDuplicateTypeNamesHandler, DuplicateTypeAction
from Autodesk.Revit.DB import ParameterFilterElement, FilterStringRule, FilterNumericValueRule, ElementFilter
from Autodesk.Revit.DB import ElementParameterFilter, LogicalOrFilter, LogicalAndFilter, FilterInverseRule, FilterRule

class Template:
    """Класс по работе с шаблонами."""
    source_doc = None
    def __init__(self, template_file_path):
        self.template_file_path = template_file_path

    def open_source(self):
        """Открывает файл с шаблонами."""
        self.source_doc = __revit__.OpenAndActivateDocument(self.template_file_path).Document
        return self.source_doc

    def find_all_view_template(self, doc):
        """
            Ищет все шаблоны у заданного документа.
            Возвращает коллекцию Title: id
        """
        view_templatates = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Views).ToElements()
        view_templatates = {i.Title: i.Id for i in view_templatates if i.IsTemplate}
        return view_templatates

    def get_similar_template(self, doc, doc_source, tempalte_name, template_sources):
        """
            Находит соответствующий шаблон в шаблонах источника.
        """
        for key, template_id in template_sources.Items():
            cur_title = doc.GetElement(template_id).Title
            if cur_title == tempalte_name[:-len(cur_title)]:
                return template_id

    def get_all_view_with_template(self, doc, template_id):
        views = [i for i in FilteredElementCollector(doc). \
            OfCategory(BuiltInCategory.OST_Views).ToElements()
            if i.ViewTemplateId == template_id]
        return views

    @classmethod
    def all_file_comparisions(cls, path, kit):
        """
            Возвращает словарь Имя шаблона: id Шаблона в файле с шаблонами.
        """
        new_dict = {}
        templ = re.compile("\d*(\.txt)$")
        digit = re.compile("\d*")
        for file in os.listdir(path):
            if cls.need_to_add(file, kit):
                res = templ.search(file)
                if res:
                    cur_id = int(digit.search(res.group(0)).group(0))
                    with open(os.path.join(path, file)) as f:
                        for line in f.readlines():
                            if line not in new_dict.keys():
                                line = line.decode('u8').replace('\n', '').replace('\r', '').strip()
                                new_dict.update({line: cur_id})
        return new_dict

    def define_kit(self, doc):
        """Определяет комплект заданного документа."""
        kit_name = ""
        temp_temp = re.compile('(КЖ)[\d.]+')
        res = temp_temp.search(doc.Title)
        kit = res.group(0)[2:]
        temp_temp = re.compile('^[\d]+')
        first_numb = temp_temp.search(kit)
        if first_numb:
            first_numb = int(first_numb.group(0))
        else:
            first_numb = None
        second_numb = temp_temp.search(kit[len(str(first_numb))+1:])
        if second_numb:
            second_numb = int(second_numb.group(0))
        else:
            second_numb = None
        return (first_numb, second_numb)

    @classmethod
    def need_to_add(cls, view_name, kit):
        """Определяет к чему принадлежит вид."""
        templ = re.compile('(\.О\.)|(\.В\.)')
        res = templ.split(view_name)[0]
        if res == 'Общ':
            return True
        if res[:2] == 'КЖ':
            res = res[2:]
            if res.isdigit():
                if int(res) == kit[0]:
                    return True
            elif res[-1].isdigit():
                if int(res[-1]) == kit[1] and kit[0] > 1 and kit[0] < 6:
                    return True

    def rename_template(self, view_name):
        """Отделяем префикс от имени шаблона."""
        templ = re.compile('(\.О\.)|(\.В\.)')
        res = templ.search(view_name)
        if res:
            res = templ.split(view_name)
            if len(res) == 4:
                res.remove(None)
                new_name = res[1][1:] + res[2]
                return new_name
        else:
            return view_name

    @classmethod
    def get_cur_date(cls):
        return '_old_' + datetime.now().strftime("%y%m%d%H%M%S")

    @classmethod
    def get_all_filters(cls, doc):
        """Получаем все фильтры из заданного документа."""
        filters = {i.Name: i.Id for i in FilteredElementCollector(doc).OfClass(ParameterFilterElement).ToElements()}
        return filters

    @classmethod
    def get_similar_filters(cls, filters_1, filters_2):
        """Проверяет сходство первой коллекции со второй по ключу."""
        similar = {}
        difrent = {}
        for i in filters_1.keys():
            if i in filters_2.keys():
                similar.update({i: filters_1[i]})
            else:
                difrent.update({i: filters_1[i]})
        return (similar, difrent)

    @classmethod
    def make_filter_users(cls, doc, filters):
        for i in filters.values():
            el = doc.GetElement(i)
            if el.Name[:6] != 'Польз.':
                el.Name = 'Польз.' + el.Name

    @classmethod
    def get_views_with_filters(cls, doc, filters):
        """Возвращает коллекцию фильтр: (вид, переопределение графики)."""
        filters = {}
        views = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Views).ToElements()
        for view in views:
            for i in view.GetFilters():
                override = view.GetFilterOverrides(i)
                visability = view.GetFilterVisibility(i)
                filter_name = doc.GetElement(i).Name
                if filter_name not in filters.keys():
                    filters.update({filter_name: []})
                filters[filter_name].append((view, override, visability))
        return filters

    @classmethod
    def rename_old_filters(cls, doc, filters):
        cur_date = cls.get_cur_date()
        for i in filters.values():
            el = doc.GetElement(i)
            el.Name += cur_date

    @classmethod
    def copy_els_form_source(cls, doc, source, els):
        """Копирует значения из dict источника в документ."""
        els = List[ElementId](els.values())
        new_filters = {}
        for i in ElementTransformUtils.CopyElements(source, els, doc, Transform.Identity, CopyPasteOptions()):
            new_filters.update({doc.GetElement(i).Name: i})
        return new_filters

    @classmethod
    def apply_new_filters(cls, doc, new_filters, old_filters):
        for filt_name, filt_items in old_filters.items():
            if filt_name[:6] != 'Польз.':
                for view, override, visability in filt_items:
                    view.AddFilter(new_filters[filt_name])
                    view.SetFilterOverrides(new_filters[filt_name], override)
                    view.SetFilterVisibility(new_filters[filt_name], visability)
    @classmethod
    def delete_els(cls, doc, els):
        for i in els.values():
            doc.Delete(i)

    @classmethod
    def delete_not_need_filters(cls, doc):
        view_filter = [i.GetFilters() for i in FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Views).ToElements()]
        all_filtes = set()
        for filter_list in view_filter:
            for filter in filter_list:
                if doc.GetElement(filter):
                    all_filtes.add(doc.GetElement(filter).Name)
        filters = [i for i in FilteredElementCollector(doc).OfClass(ParameterFilterElement).ToElements()]
        for i in filters:
            if i.Name not in all_filtes:
                doc.Delete(i.Id)

    @classmethod
    def delete_not_need_template(cls, doc):
        views = set([i.ViewTemplateId for i in FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Views).ToElements() if i.ViewTemplateId])
        templates = set([i for i in FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Views).ToElementIds() if doc.GetElement(i).IsTemplate and i not in views and doc.GetElement(i).Title[:6] != "Польз."])
        for i in templates:
            doc.Delete(i)
