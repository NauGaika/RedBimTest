import re
import os
from math import pi

from System.Collections.Generic import List

from Autodesk.Revit.DB import BuiltInCategory, BuiltInParameter, Transaction, FilteredElementCollector, ElementId, Category
from Autodesk.Revit.DB import ElementTransformUtils, Transform, CopyPasteOptions, CategorySet, InstanceBinding, SharedParameterElement
from Autodesk.Revit.DB import IDuplicateTypeNamesHandler, DuplicateTypeAction
from Autodesk.Revit.DB import ParameterFilterElement, FilterStringRule, FilterNumericValueRule, ElementFilter
from Autodesk.Revit.DB import ElementParameterFilter, LogicalOrFilter, LogicalAndFilter, FilterInverseRule, FilterRule

from common_scripts.Template import Template

class Duplicator:
    comparison_paths = '\\\\picompany.ru\\pikp\\Dep\\LKP4\\WORK\\Шаблоны видов\\Сопоставления'
    template_file_path = '\\\\picompany.ru\\pikp\\Dep\\LKP4\\WORK\\Шаблоны видов\\Шаблоны видов.rvt'
    def __init__(self,  doc):
        self.doc_source = None
        for i in __revit__.Application.Documents:
            if 'Шаблоны видов' in i.Title:
                self.doc_source = i
        if not self.doc_source:
            self.doc_source = __revit__.OpenAndActivateDocument(self.template_file_path).Document
        t = Transaction(doc, 'Перегрузка шаблонов')
        t.Start()
        self.doc = doc
        self.kit = self.define_kit(self.doc)
        echo('_________________', 'Комплект чертежей ' + self.kit + ' тип: ' + self.kit_name)
        echo('_____________________', 'Удаляем неиспользуемые шаблоны')
        Template.delete_not_need_template(self.doc)
        echo('_________________', 'Получаем все фильтры текущего документа и файла с шаблонами')
        self.doc_filters = Template.get_all_filters(self.doc)
        self.source_filters = Template.get_all_filters(self.doc_source)
        echo('_________________', 'Находим одинаковые и разные фильтры')
        self.similar_filters, self.diffrent_filters = Template.get_similar_filters(self.doc_filters, self.source_filters)
        echo('_________________', 'Добавляем приставку Польз.')
        Template.make_filter_users(self.doc, self.diffrent_filters)
        echo('_________________', 'Находим виды с пересекающимися фильтрами и их переопределения')
        self.filter_view_dict = Template.get_views_with_filters(self.doc, self.similar_filters)
        echo('_________________', 'Переименовываем имеющиеся фильтры')
        Template.rename_old_filters(self.doc, self.similar_filters)
        echo('_________________', 'Копируем фильтры')
        self.new_filters = Template.copy_els_form_source(self.doc, self.doc_source, self.source_filters)
        echo('_________________', 'Применяем фильтры с переопределением')
        Template.apply_new_filters(self.doc, self.new_filters, self.filter_view_dict)
        echo('_________________', 'Удаляем старые фильтры')
        Template.delete_els(self.doc, self.similar_filters)
        self.all_templates_names = Template.all_file_comparisions(self.comparison_paths, (self.first_numb, self.second_numb))
        self.source_view_templatates = self.templates_need_to_add(self.doc_source, self.find_all_view_template(self.doc_source))
        self.view_templatates = self.find_all_view_template(self.doc)
        echo('_____________________', 'Сравниваем шаблоны')
        self.compared_params = self.compare_templates(self.source_view_templatates, self.view_templatates)
        echo('_____________________', 'Ищем виды, к которым применен шаблон')
        self.view_with_template = self.get_views_with_templates(self.doc, self.compared_params)
        echo('_____________________', 'Удаляем шаблоны у видов которые нужно заменить')
        self.delete_template_from_view(self.doc, self.view_with_template.values())
        echo('_____________________', 'Переименовываем шаблоны у текущего документа')
        self.rename_old_templates(self.doc, self.view_templatates, self.source_view_templatates)
        echo('_____________________', 'Копируем шаблон из файла с шаблонами')
        self.copy_templates(self.doc, self.doc_source, self.source_view_templatates)
        echo('_____________________', 'Применяем шаблоны обратно')
        self.view_templatates = self.find_all_view_template(self.doc)
        self.apply_template(self.doc, self.view_templatates, self.view_with_template)
        echo('_____________________', 'Переименовываем шаблоны')
        self.rename_all_template(self.view_templatates)
        Template.delete_not_need_filters(self.doc)
        echo('_____________________', 'Изменение фильтр КЖ для комплекта ' + self.kit)
        self.change_filter_kg(self.doc)
        t.Commit()

    def templates_need_to_add(self, doc, templates):
        new_templates = {}
        for template_id in templates.values():
            template = doc.GetElement(template_id)
            templ = re.compile('(\.О\.)|(\.В\.)')
            res = templ.split(template.Title)[0]
            if template.IsTemplate:
                if res == 'Общ':
                    new_templates.update({template.Title: template.Id})
                if res[:2] == 'КЖ':
                    res = res[2:]
                    if res.isdigit():
                        if int(res) == self.first_numb:
                            new_templates.update({template.Title: template.Id})
                    elif res[-1].isdigit():
                        s_n = self.second_numb
                        if s_n%2 == 0:
                            s_n = 2
                        else:
                            s_n = 1
                        if int(res[-1]) == s_n and self.first_numb > 1 and self.first_numb < 6:
                            new_templates.update({template.Title: template.Id})
        return new_templates

    def define_kit(self, doc):
        kit_name = ""
        temp_temp = re.compile('(КЖ)[\d.]+')
        res = temp_temp.search(doc.Title)
        kit = res.group(0)[2:]
        temp_temp = re.compile('^[\d]+')
        first_numb = temp_temp.search(kit)
        if first_numb:
            self.first_numb = int(first_numb.group(0))
        else:
            self.first_numb = None
        second_numb = temp_temp.search(kit[len(str(self.first_numb))+1:])
        if second_numb:
            self.second_numb = int(second_numb.group(0))
        else:
            self.second_numb = None
        if self.first_numb == 1:
            self.kit_name = 'Фундаменты'
        elif self.first_numb == 2 and self.second_numb == 1:
            self.kit_name = 'Вертикальные конструкции техподполья'
        elif self.first_numb == 2 and self.second_numb == 2:
            self.kit_name = 'Горизонтальные конструкции техподполья'
        elif self.first_numb == 3 and self.second_numb == 1:
            self.kit_name = 'Вертикальные конструкции первого этажа'
        elif self.first_numb == 3 and self.second_numb == 2:
            self.kit_name = 'Горизонтальные конструкции первого этажа'
        elif self.first_numb == 4 and self.second_numb % 2 == 1:
            self.kit_name = 'Вертикальные конструкции типового этажа'
        elif self.first_numb == 4 and self.second_numb % 2 == 0:
            self.kit_name = 'Горизонтальные конструкции типового этажа'
        elif self.first_numb == 6:
            self.kit_name = 'Лестницы'
        return kit

    def find_all_view_template(self, doc):
        view_templatates = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Views).ToElements()
        view_templatates = {i.Title: i.Id for i in view_templatates if i.IsTemplate}
        return view_templatates

    def compare_templates(self, source, current):
        common_templates = {}
        for key_s, i_s in source.items():
            view_names = self.get_file_if_exists(key_s, i_s)
            for key_c, i_k in current.items():
                if key_c in view_names:
                    echo("Найден одинаковый шаблон " + key_s + ' и ' + key_c)
                    common_templates.update({key_c: key_s})
        return common_templates

    def get_file_if_exists(self, name, v_id):
        file_name = os.path.join(self.comparison_paths, name + "_" + str(v_id.IntegerValue) + '.txt')
        # echo(file_name)
        view_names = []
        if os.path.exists(file_name):
            with open(file_name) as f:
                for line in f.readlines():
                    view_names.append(line.decode('u8').replace('\n', '').replace('\r', '').strip())
        else:
            view_names.append(name)
            view_names.append(self.rename_template(name))
        return view_names

    def get_views_with_templates(self, doc, templates):
        views = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Views).ToElementIds()
        views = [i for i in views if doc.GetElement(i).ViewTemplateId.IntegerValue > 0]
        view_with_template = {}
        for i in views:
            view = doc.GetElement(i)
            template_title = doc.GetElement(view.ViewTemplateId).Title
            if template_title in templates.keys():
                if templates[template_title] not in view_with_template.keys():
                    view_with_template.update({templates[template_title]: [i]})
                else:
                    view_with_template[templates[template_title]].append(i)
        return view_with_template

    def delete_template_from_view(self, doc,  view_ids):
        for i in view_ids:
            for b in i:
                doc.GetElement(b).ViewTemplateId = ElementId.InvalidElementId

    def rename_old_templates(self, doc, templates, source_template):
        """Переименовываем шаблоны в старые."""
        for key, i in templates.items():
            temp_name = doc.GetElement(i).get_Parameter(BuiltInParameter.VIEW_NAME)
            if temp_name.AsString()[:6] != "Польз.":
                if temp_name.AsString() in self.all_templates_names.keys():
                    doc.Delete(i)
                else:
                    temp_name.Set('Польз.' + temp_name.AsString())

    def copy_templates(self, doc, source, templates):
        els = List[ElementId](templates.values())
        ElementTransformUtils.CopyElements(source, els, doc, Transform.Identity, CopyPasteOptions())

    def apply_template(self, doc, templates, views_dict):
        for key, views in views_dict.items():
            cur_template = templates[key]
            for view in views:
                # echo('Применяем ' + key + ' ' + doc.GetElement(view).Title)
                doc.GetElement(view).ViewTemplateId = cur_template

    def rename_all_template(self, templates):
        for name, i in templates.items():
            if name:
                self.doc.GetElement(i).get_Parameter(BuiltInParameter.VIEW_NAME).Set(self.rename_template(name))

    def rename_template(self, view_name):
        if view_name[:6] != 'Польз.':
            templ = re.compile('(\.О\.)|(\.В\.)')
            res = templ.search(view_name)
            if res:
                res = templ.split(view_name)
                if len(res) == 4:
                    res.remove(None)
                    new_name = res[1][1:] + res[2]
                    return new_name
        return view_name

    def change_filters(self, filters):
        for i in filters:
            if isinstance(i, LogicalAndFilter) or isinstance(i, LogicalOrFilter):
                self.change_filters(i.GetFilters())
            if isinstance(i, ElementParameterFilter):
                for b in i.GetRules():
                    tk = b
                    if isinstance(b, FilterInverseRule):
                        tk = b.GetInnerRule()
                    if isinstance(tk, FilterStringRule):
                        tk.RuleString = '-' + self.kit + '-'

    def change_filter_kg(self, doc):
        els = FilteredElementCollector(doc).OfClass(ParameterFilterElement).ToElements()
        pattern = re.compile('КЖ')
        els = [el for el in els if pattern.search(el.Name)]
        for i in els:
            i.SetElementFilter(self.recurse_change_filter(i.GetElementFilter()))

    def recurse_change_filter(self, filter):
        """Рекурсивное изменение текстовых фильтров."""
        if isinstance(filter, LogicalAndFilter):
            res =  LogicalAndFilter(self.recurse_change_filter(filter.GetFilters()))
            return res
        elif isinstance(filter, LogicalOrFilter):
            res = LogicalOrFilter(self.recurse_change_filter(filter.GetFilters()))
            return res
        elif isinstance(filter, ElementParameterFilter):
            arr = List[FilterRule]()
            for i in filter.GetRules():
                if isinstance(i, FilterInverseRule):
                    i = i.GetInnerRule()
                    cur_kit = self.cur_rule(i.RuleString)
                    i.RuleString = cur_kit
                    i = FilterInverseRule(i)
                if isinstance(i, FilterStringRule):
                    cur_kit = self.cur_rule(i.RuleString)
                    i.RuleString = cur_kit
                arr.Add(i)
            res = ElementParameterFilter(arr)
            return res
        elif isinstance(filter, List[ElementFilter]):
            arr = List[ElementFilter]()
            for i in filter:
                arr.Add(self.recurse_change_filter(i))
            return arr

    def cur_rule(self, rule_string):
        cur_kit = self.kit
        first_num = int(cur_kit[0])
        if rule_string == '-комплект-':
            return '-' + cur_kit + '-'
        if rule_string == '-комплект выше-':
            cur_kit = str(first_num + 1) + cur_kit[1:]
            return '-' + cur_kit + '-'
        if rule_string == '-комплект ниже-':
            cur_kit = str(first_num - 1) + cur_kit[1:]
            return '-' + cur_kit + '-'
        return rule_string


active_doc = __revit__.ActiveUIDocument.Document
dp = Duplicator(active_doc)
