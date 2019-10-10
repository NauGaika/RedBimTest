import re
from Autodesk.Revit.DB import FilteredElementCollector, ViewSection
from Autodesk.Revit.UI.Selection import ObjectType
from Autodesk.Revit.Exceptions import OperationCanceledException
from common_scripts.get_elems.RB_selections import RB_selections
from Autodesk.Revit.DB import BuiltInCategory, BuiltInParameter, Transaction
from Autodesk.Revit.UI import ExternalEvent, IExternalEventHandler

ViewSect = 'Орг.ГруппаВида'


FORM.Start(6)
inp = FORM.GetLines(1).add_textbox('тип вида', 'Разрез')
FORM.GetLines(1).add_label('Префикс имени вида')
inp.Height = 24
cb = FORM.GetLines(2).add_checked_list_box('Добавить заголовок на листе', [('Да', True)])
FORM.GetLines(2).add_label('Задать имя на листе')
cb.Height = 24
set_of_view = FORM.GetLines(3).add_textbox('Комплект чертежей', '')
set_of_view.Height = 24
FORM.GetLines(3).add_label('Орг.КомплектЧертежей')
new_name = FORM.GetLines(4).add_textbox('Имя вида', '')
new_name.Height = 24
FORM.GetLines(4).add_label('Имя вида')
new_name_sheet = FORM.GetLines(5).add_textbox('Имя вида на листе', '')
new_name_sheet.Height = 24
FORM.GetLines(5).add_label('Имя вида на листе')
but2 = FORM.GetLines(6).add_button('Отмена')
but = FORM.GetLines(6).add_button('Добавить')

doc = __revit__.ActiveUIDocument.Document
all_view_name = []
views = FilteredElementCollector(doc).OfClass(ViewSection ).ToElements()
all_view_name = [view.get_Parameter(BuiltInParameter.VIEW_NAME).AsString()for view in views]

cat_list = [BuiltInCategory.OST_Floors, BuiltInCategory.OST_Stairs,
            BuiltInCategory.OST_StructuralFraming,
            BuiltInCategory.OST_StructuralColumns, BuiltInCategory.OST_Walls,
            BuiltInCategory.OST_StructuralFoundation]

def get_level(mark):
    """Вычленяет комплект чертежей."""
    pattern = re.compile('[А-Яа-я]+-\d+[.\d+]+')
    digit = re.compile("\d+[.\d+]+")
    text = pattern.findall(mark)
    if text:
        level = digit.findall(text[0])
        if level:
            return 'КЖ' + level[0]
    return 'Общ'

def calculate_new_name(constr):
    view = doc.ActiveView #Текущий вид
    constr_mark = constr.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).AsString() #Марка конструкции
    post = inp.GetValue() #Наименование вида
    view_cat = view.GetParameters(ViewSect)[0].AsString() #Орг.ВидРаздел
    name = constr_mark + ' ' + post
    new_name_sheet.Text = post
    new_name.Text = add_prefix_if_need(name)
    if view.GetParameters('Орг.КомплектЧертежей')[0].IsReadOnly:
        set_of_view.Text = 'Орг.КомплектЧертежей заблокирован в шаблоне'
    else:
        set_of_view.Text = get_level(constr_mark)

def add_prefix_if_need(name):
    if name in all_view_name:
        number = 0
        prefix = ''
        while True:
            number += 1
            new_name = name + ' ' + str(number)
            if new_name not in all_view_name:
                name = new_name
                break
    return name

def close_form():
    FORM.Close()

class ExternalEventExample(IExternalEventHandler):
    def Execute(self, app):
        doc = app.ActiveUIDocument.Document
        view = doc.ActiveView
        p_view_set = view.GetParameters('Орг.КомплектЧертежей')[0]
        p_view_description = view.get_Parameter(BuiltInParameter.VIEW_DESCRIPTION)
        p_view_name = view.get_Parameter(BuiltInParameter.VIEW_NAME)
        with Transaction(doc, 'Имя вида') as t:
            t.Start()
            if not p_view_set.IsReadOnly:
                p_view_set.Set(set_of_view.Text)
            if cb.GetValue()['Да']:
                p_view_description.Set(new_name_sheet.Text)
            p_view_name.Set(new_name.Text)
            t.Commit()
        close_form()
    def GetName(self):
        return 'New name'

def test():
    FORM.exEvent.Raise()

but.AddFunction(test)
but2.AddFunction(close_form)
handler = ExternalEventExample()
exEvent = ExternalEvent.Create(handler)
constr = RB_selections.pick_element_by_category(cat_list)
inp.AddFunction(calculate_new_name, constr)
calculate_new_name(constr)
FORM.Create(exEvent)
