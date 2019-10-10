from Autodesk.Revit.DB import Transaction, BuiltInCategory, Category, CategorySet, TypeBinding, FilteredElementCollector, Viewport, BuiltInParameter
from Autodesk.Revit.UI import IExternalEventHandler, ExternalEvent

doc = __revit__.ActiveUIDocument.Document
FORM.Start(2)

view_number = FORM.GetLines(1).add_textbox('Номер вида', '1')
FORM.GetLines(1).add_label('Номер вида')
view_number.Height = 24
but_create = FORM.GetLines(2).add_button('Переименовать')
but_cancel = FORM.GetLines(2).add_button('Отмена')

FORM.calculate_size()

viewport = [doc.GetElement(elId) for elId in __revit__.ActiveUIDocument.Selection.GetElementIds()]

class rename_view(IExternalEventHandler):
    def Execute(self, app):
        t = Transaction(doc, 'Переименовать вид')
        t.Start()
        cur_numb = viewport.get_Parameter(BuiltInParameter.VIEWPORT_DETAIL_NUMBER)
        cur_numb_value = cur_numb.AsString()
        
        sheet = viewport.SheetId
        views = FilteredElementCollector(doc, sheet).OfClass(Viewport).ToElements()
        for i in views:
            if i.get_Parameter(BuiltInParameter.VIEWPORT_DETAIL_NUMBER).AsString() == view_number.GetValue():
                i.get_Parameter(BuiltInParameter.VIEWPORT_DETAIL_NUMBER).Set(to_str(i.Id.IntegerValue))
                cur_numb.Set(to_str(view_number.GetValue()))
                i.get_Parameter(BuiltInParameter.VIEWPORT_DETAIL_NUMBER).Set(cur_numb_value)
                break
        else:
            cur_numb.Set(to_str(view_number.GetValue()))
        t.Commit()
        FORM.Close()

    def GetName(self):
        return 'New name'


def start():
    FORM.exEvent.Raise()

if viewport:
    viewport = viewport[0]
    if isinstance(viewport, Viewport):
        view_number.Text = viewport.get_Parameter(BuiltInParameter.VIEWPORT_DETAIL_NUMBER).AsString()
        handler = rename_view()
        exEvent = ExternalEvent.Create(handler)
        but_cancel.AddFunction(FORM.Close)
        but_create.AddFunction(start)
        FORM.Create(exEvent)
    else:
        message('Выберете видовой экран')
else:
    message('Выберете видовой экран')


