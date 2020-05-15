# coding: utf8
"""Выносим вид на лист"""
from Autodesk.Revit.DB import FilteredElementCollector, ViewSheet, Viewport, XYZ, ElementId, Transaction
from System.Drawing import Point
from System.Windows.Forms import Application, Button, ComboBox, Form, Label
from Autodesk.Revit.UI import ExternalEvent, IExternalEventHandler

doc = __revit__.ActiveUIDocument.Document

sheets = FilteredElementCollector(doc).OfClass(ViewSheet).ToElements()
sheets = {"{} - {}".format(i.SheetNumber, i.Name): i.Id for i in sheets}


class add_viewport(IExternalEventHandler):
    def __init__(self, form):
        self.form = form

    def Execute(self, app):
        with Transaction(doc, "Разместить на лист") as t:
            t.Start()
            if Viewport.CanAddViewToSheet(doc, sheets[self.form.combo_box.SelectedItem], doc.ActiveView.Id):
                Viewport.Create(doc, sheets[self.form.combo_box.SelectedItem], doc.ActiveView.Id, XYZ(-1,1,0))
                # message("Вид '{}'' размещен на лист '{}'".format(doc.ActiveView.Title, self.form.combo_box.SelectedItem))
            else:
                message("Вид '{}'' не может быть добавлен на лист '{}'".format(doc.ActiveView.Title, self.form.combo_box.SelectedItem))
            t.Commit()

    def GetName(self):
        return 'New name'

class My_Form(Form):
    def __init__(self, items):
        self.exEvent = None
        self.Width = 360
        self.Height = 140
        self.combo_box = ComboBox()
        self.combo_box.Width = 300
        self.combo_box.Location = Point(20, 30)
        items = list(items)
        items.sort()
        for i in items:
            self.combo_box.Items.Add(i)
        self.combo_box.SelectedIndex = 0
        self.label = Label()
        self.label.Text = "Выберете лист на который нужно добавить текущий вид"
        self.label.Width = 400
        self.label.Location = Point(20, 10)

        self.button = Button()
        self.button.Width = 300
        self.button.Text = "Расположить"
        self.button.Location = Point(20, 60)
        self.button.Click += self.run
        self.Controls.Add(self.combo_box)
        self.Controls.Add(self.label)
        self.Controls.Add(self.button)

    def run(self, hand, e):
        self.exEvent.Raise()
        self.Close()





form = My_Form(sheets.keys())
handler = add_viewport(form)
exEvent = ExternalEvent.Create(handler)
form.exEvent = exEvent

form.Show()