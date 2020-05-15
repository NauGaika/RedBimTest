
# import os
from System.Windows.Forms import Application, Form, Label, ListBox, SelectionMode, Button, DockStyle, AnchorStyles, ComboBox
from System.Drawing import Point, ContentAlignment

from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, Transaction, SharedParameterElement, ParameterElement, ParameterType
from Autodesk.Revit.DB import LabelUtils, BuiltInParameterGroup, ExternalDefinitionCreationOptions
from Autodesk.Revit.Exceptions import InvalidOperationException, ArgumentException
from Autodesk.Revit.UI import ExternalEvent, IExternalEventHandler

from tempfile import gettempdir
import os

import re

doc = __revit__.ActiveUIDocument.Document

class Execute_change_group(IExternalEventHandler):
    def __init__(self):
        self._selected_group = None
        self._selected_params = None
        self._shared_param_group = None
        self.prev_path = ""

    def Execute(self, app):
        with Transaction(doc, "Все параметры экземпляра") as t:
            t.Start()
            self.fm = doc.FamilyManager
            for fPar in self._selected_params:
                definition = fPar.Definition
                isShared = fPar.IsShared
                isInstance = fPar.IsInstance
                pType = definition.ParameterType
                if isShared:
                    edef = self.create_parameter(definition.Name, pType)
                    fPar = self.fm.ReplaceParameter(fPar, definition.Name + "1", self._selected_group, isInstance)
                    self.fm.ReplaceParameter(fPar, edef, self._selected_group, isInstance)
                    echo("Перенесен параметр " + definition.Name)
                else:
                    edef = self.create_parameter(definition.Name + "1", pType)
                    fPar = self.fm.ReplaceParameter(fPar, edef, self._selected_group, isInstance)
                    self.fm.ReplaceParameter(fPar, definition.Name, self._selected_group, isInstance)
                    echo("Перенесен параметр " + definition.Name)

            app.SharedParametersFilename = self.prev_path
            os.remove(self.file_path)
            t.Commit()

    @property
    def shared_param_group(self):
        if not self._shared_param_group:
            app = __revit__.Application
            self.prev_path = app.SharedParametersFilename
            self.file_path = gettempdir() + "\\test.txt"
            f = open(file_path, "w+")
            f.close()
            app.SharedParametersFilename = file_path
            file = app.OpenSharedParameterFile()
            file.Groups.Create("temp")
            gr = file.Groups.Item["temp"]
            self._shared_param_group = gr
        return self._shared_param_group

    def create_parameter(self, param_name, param_type):
        opt = ExternalDefinitionCreationOptions(param_name, param_type)
        el = self.shared_param_group.Definitions.Create(opt)
        return el

#os.remove(file_path)
#app.SharedParametersFilename = prev_file

    def GetName(self):
        return 'Change parameter type'

class SelectParameter(Form):
    _all_param_group = {}

    def __init__(self):
        self.fm = doc.FamilyManager
        self._all_param_names = None
        
        self.Text = 'Параметры'
        self.Name = 'Select Parameters'
        self.Width = 400
        self.Height = 450
        
        self.title = Label()
        self.title.Text = "Выберете параметры"
        self.title.Height = 30
        self.title.TextAlign = ContentAlignment.MiddleCenter
        self.title.Dock = DockStyle.Top

        self.label = Label()
        self.label.Text = "Выберете новую группу параметров"
        self.label.Height = 30
        self.label.TextAlign = ContentAlignment.MiddleCenter
        self.label.Dock = DockStyle.Top
        
        self.listbox = ListBox()
        self.listbox.MultiColumn = False
        self.listbox.SelectionMode = SelectionMode.MultiExtended
        self.listbox.BeginUpdate()
        params = list(self.all_param_names.keys())
        params.sort()
        for i in params:
            self.listbox.Items.Add(i)
        self.listbox.EndUpdate()
        self.listbox.Height = 270
        self.listbox.Location = Point(0, 30)
        self.listbox.Dock = DockStyle.Top

        self.combobox = ComboBox()
        els = list(self.all_param_group.keys())
        els.sort()
        for i in els:
            self.combobox.Items.Add(i)
        self.combobox.Location = Point(0, 300)
        self.combobox.Dock = DockStyle.Top

        self.button = Button()
        self.button.Text = "Перенести"
        self.button.Dock = DockStyle.Top
        self.button.Click += self.change_param_group

        self.Controls.Add(self.button)
        self.Controls.Add(self.combobox)
        self.Controls.Add(self.label)
        self.Controls.Add(self.listbox)
        self.Controls.Add(self.title)

        self.handler = Execute_change_group()
        self.exEvent = ExternalEvent.Create(self.handler)

    @property
    def all_param_names(self):
        if self._all_param_names is None:

            self._all_param_names = {"({}) {}".format(LabelUtils.GetLabelFor(i.Definition.ParameterGroup), i.Definition.Name): i for i in self.fm.GetParameters()}
        return self._all_param_names

    @property
    def all_param_group(self):
        if not self.__class__._all_param_group:
            els = {LabelUtils.GetLabelFor(getattr(BuiltInParameterGroup, i)): getattr(BuiltInParameterGroup, i) for i in dir(BuiltInParameterGroup) if i[0:2] == "PG"}
            self.__class__._all_param_group = els
        return self.__class__._all_param_group

    
    def change_param_group(self, arg, prop):
        self.handler._selected_params = [self.all_param_names[i] for i in self.listbox.SelectedItems]
        self.handler._selected_group = self.all_param_group[self.combobox.SelectedItem]
        self.exEvent.Raise()
        self.Close()


form = SelectParameter()
Application.Run(form)