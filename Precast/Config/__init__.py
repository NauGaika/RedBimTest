# -*- coding: utf-8 -*-
from common_scripts import echo
from .Parameters import project_parameters


class ParameterChecker(object):
    "Класс добавления параметров."

    def __init__(self, doc):
        self.doc = doc
        self.parameters = project_parameters
        self.check_parameters()

    def check_parameters(self):
        app = __revit__.Application
        shared_par_file = app.OpenSharedParameterFile()
        pb = self.doc.ParameterBindings
        for i in shared_par_file.Groups:
            for definition in i.Definitions:
                if definition.Name in self.parameters.keys():
                    param = self.parameters[definition.Name]
                    doc_cats = [self.doc.Settings.Categories.get_Item(
                        i) for i in param["categoryes"]]
                    if pb.Contains(definition):
                        parameter_bind = pb.Item[definition]
                        change_cats = []
                        for cat in doc_cats:
                            if not parameter_bind.Categories.Contains(cat):
                                parameter_bind.Categories.Insert(cat)
                                change_cats.append(cat.Name)
                        if change_cats:
                            echo("Для параметра {} добавлены категории {}".format(
                                definition.Name, ", ".join(change_cats)))
                            pb.ReInsert(definition, parameter_bind)
                    else:
                        cat_set = app.Create.NewCategorySet()
                        for cat in doc_cats:
                            cat_set.Insert(cat)
                        nib = app.Create.NewInstanceBinding(cat_set)
                        pb.Insert(definition, nib, param["group"])
                        echo("Добавлен параметр {} для категорий {}".format(
                            definition.Name, ", ".join([i.Name for i in doc_cats])))
                # else:
                #     echo("Не найден параметр {}".format(definition.Name))

