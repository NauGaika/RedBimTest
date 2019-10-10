import os
import re
from Autodesk.Revit.DB import BuiltInCategory, BuiltInParameter, Transaction, \
FilteredElementCollector, ElementId, Category
from System import String

class FilterStructure:
    """Создает структуру для шаблонов и их сопоставлений."""
    doc = active_doc = __revit__.ActiveUIDocument.Document
    comparison_paths = '\\\\picompany.ru\\pikp\\Dep\\LKP4\\WORK\\Шаблоны видов\\Сопоставления'
    def __init__(self):
        """Начинаем работу с шаблонами."""
        if self.doc.PathName == os.path.join(os.path.dirname(self.comparison_paths), "Шаблоны видов.rvt"):
            self.templates = self.get_templates()
            self.templates_id = {i: k for k, i in self.templates.items()}
            if os.path.exists(self.comparison_paths):
                self.compare_exists_names()
                self.create_structure()
                self.delete_not_need()
        else:
            echo("Данный скрипт работает только с " + os.path.join(os.path.dirname(self.comparison_paths), "Шаблоны видов.rvt"))

    def get_templates(self):
        """Получаем все шаблоны из текущего документа в виде id_Имя шаблона."""
        filters = FilteredElementCollector(self.doc).OfCategory(
            BuiltInCategory.OST_Views).ToElements()
        filters = {i.Title: i.Id.IntegerValue for i in filters if i.IsTemplate}
        return filters

    def delete_not_need(self):
        all_files = os.listdir(self.comparison_paths)
        temp_name = re.compile('_\d{5,}$')
        all_files = {temp_name.sub('', i[:-4]): i for i in all_files if i[-4:] == '.txt'}
        for i in all_files.keys():
            if i not in self.templates.keys():
                os.remove(os.path.join(self.comparison_paths, all_files[i]))
                echo('Удален файл {}'.format(i))


        exists_templates = self.templates.keys()

    def compare_exists_names(self):
        all_files = os.listdir(self.comparison_paths)
        all_files = [i for i in all_files if i[-4:] == '.txt']
        temp_id = re.compile('\d{5,}$')
        temp_name = re.compile('_\d{5,}$')
        for k in all_files:
            i = k[:-4]
            name = temp_name.sub('', i)
            v_id = temp_id.findall(i)
            if v_id:
                v_id = int(v_id[0])
            if name in self.templates.keys():
                if self.templates[name] != v_id:
                    echo('У шаблона '+ name + ' поменялся id ' + to_str(v_id) + ' на ' + to_str(self.templates[name]))
                    os.rename(
                        os.path.join(self.comparison_paths, k),
                        os.path.join(self.comparison_paths, name + '_' +  to_str(self.templates[name]) + '.txt')
                    )
            if v_id in self.templates_id.keys():
                if self.templates_id[v_id] != name:
                    with open(os.path.join(self.comparison_paths, k) ,"a") as file:
                        file.write((name + "\n").encode('u8'))
                        if self.templates_id[v_id] != self.split_by_type(self.templates_id[v_id]):
                            file.write((self.split_by_type(self.templates_id[v_id]) + "\n").encode('u8'))
                        file.close()
                    new_name = self.templates_id[v_id] + '_' +  to_str(v_id) + '.txt'
                    if not os.path.exists(os.path.join(self.comparison_paths, new_name)):
                        echo('Шаблон переименован с ' + k + ' в ' + new_name)
                        os.rename(
                            os.path.join(self.comparison_paths, k),
                            os.path.join(self.comparison_paths, new_name)
                        )


    def concate_name(self, cort):
        return cort + '_' + str(self.templates[cort])

    def create_structure(self):
        # for template in self.templates:
        if os.path.isdir(self.comparison_paths):
            echo('','Путь ' + self.comparison_paths + ' существует')
            for i in self.templates.keys():
                template_path = os.path.join(self.comparison_paths, self.concate_name(i) + '.txt')
                if not os.path.exists(template_path):
                    echo('Создаем файл ' + self.concate_name(i))
                    with open(template_path,"w+") as file:
                        self.create_start_structure(file, i)
                        file.close()
        else:
            echo('Путь ' + self.comparison_paths + ' не существует')

    def create_start_structure(self, file, name):
        file.write((self.split_by_type(name) + "\n").encode('u8'))
        file.write((name + "\n").encode('u8'))

    def split_by_type(self, name):
        templ = re.compile('(\.О\.)|(\.В\.)')
        res = templ.search(name)
        if res:
            res = templ.split(name)
            if len(res) == 4:
                res.remove(None)
                new_name = res[1][1:] + res[2]
                return new_name
        else:
            return name

FilterStructure()
