
# import os
from System.Windows.Forms import Application, Form, Label, ListBox, SelectionMode, Button, DockStyle, AnchorStyles
from System.Drawing import Point, ContentAlignment

from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, Transaction, SharedParameterElement, ParameterElement, ParameterType
from Autodesk.Revit.Exceptions import InvalidOperationException, ArgumentException
from Autodesk.Revit.UI import ExternalEvent, IExternalEventHandler
import re

doc = __revit__.ActiveUIDocument.Document
# fm = doc.FamilyManager

class Execute_change_type(IExternalEventHandler):
    def __init__(self):
        self.graph = None
        # self.res = ""

    def Execute(self, app):
        with Transaction(doc, "Все параметры экземпляра") as t:
            t.Start()
            self.fm = doc.FamilyManager
            echo("Параметры теперь параметры экземпляра")
            for graph in self.graph:
                self.recur_change_type(graph)
            t.Commit()

    def recur_change_type(self, res):
        if res["dep"]:
            for i in res["dep"]:
                self.recur_change_type(i)
        fp = self.fm.get_Parameter(res["param"])
        self.fm.MakeInstance(fp)
        echo(res["param"])
        
    def GetName(self):
        return 'Change parameter type'

class SelectParameter(Form):

    def __init__(self):
        self.fm = doc.FamilyManager
        self._all_param_names = None
        
        self.Text = 'Параметры'
        self.Name = 'Select Parameters'
        self.Width = 210
        self.Height = 400
        
        self.title = Label()
        self.title.Text = "Выберете параметры"
        self.title.Height = 30
        self.title.TextAlign = ContentAlignment.MiddleCenter
        self.title.Dock = DockStyle.Top
        
        self.combobox = ListBox()
        self.combobox.MultiColumn = False
        self.combobox.SelectionMode = SelectionMode.MultiExtended
        self.combobox.BeginUpdate()
        for i in self.all_param_names:
            self.combobox.Items.Add(i)
        self.combobox.EndUpdate()
        self.combobox.Height = 270
        self.combobox.Location = Point(0, 30)
        self.combobox.Dock = DockStyle.Top
        
        self.button = Button()
        self.button.Text = "Выполнить"
        self.button.Dock = DockStyle.Top
        self.button.Click += self.change_param_type
        
        
        self.Controls.Add(self.button)
        self.Controls.Add(self.combobox)
        self.Controls.Add(self.title)
        
        self.handler = Execute_change_type()
        self.exEvent = ExternalEvent.Create(self.handler)

    @property
    def all_param_names(self):
        if self._all_param_names is None:
            self._all_param_names = [i.Definition.Name for i in self.fm.GetParameters() if not i.IsInstance]
        return self._all_param_names
    
    @property
    def graph(self):
        return [self.depend_of_param(i) for i in self.combobox.SelectedItems]

    def depend_of_param(self, param):
        res = {
            "param": param,
            "dep": []
        }
        for cur_param in self.all_param_names:
            if cur_param == param:
                continue
            f_param = self.fm.get_Parameter(cur_param)
            if f_param.IsDeterminedByFormula:
                templ = re.compile("(^({0})[^A-Za-zА-Яа-я0-9_])|([^A-Za-zА-Яа-я0-9_]({0})[^A-Za-zА-Яа-я0-9_])|(({0})$)|(\[({0})\])".format(param))
                if templ.search(f_param.Formula):
                    res["dep"].append(self.depend_of_param(cur_param))
        return res

    def change_param_type(self, arg, prop):
        self.handler.graph = self.graph
        self.exEvent.Raise()
        self.Close()
        

form = SelectParameter()
Application.Run(form)