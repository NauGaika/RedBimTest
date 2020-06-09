from Autodesk.Revit.DB import Transaction, FilteredElementCollector, \
BuiltInCategory, ElementId, IFamilyLoadOptions, FamilySource 
import time

docs = __revit__.Application.Documents
templ_doc = None
templ_view = None
for i in docs:
    if "Чистый СЭМ" in i.Title:
        templ_doc = i
        templ_view = templ_doc.GetElement(ElementId(8848))
        break

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document

cur_view = uidoc.ActiveGraphicalView


class fm_load_opt(IFamilyLoadOptions):
    def OnFamilyFound(self, fam_in_use, bool_):
        # bool_.Value = True
        return True

    def OnSharedFamilyFound(self, fam, fam_in_use, fam_source, over_par_val):
        return True

start_time = time.time()

els = FilteredElementCollector(templ_doc, templ_view.Id).ToElements()
res = set()
for i in els:
    if hasattr(i, "Symbol"):
        symb = i.Symbol
        if hasattr(symb, "Family"):
            res.add(symb.Family.Id.IntegerValue)
    elif hasattr(i, "GetTypeId"):
        type_ = templ_doc.GetElement(i.GetTypeId())
        if type_ and hasattr(type_, "Family"):
            res.add(type_.Family.Id.IntegerValue)

els = [templ_doc.GetElement(ElementId(i)) for i in res]

count = len(els)
pos = 0
for i in els:
    pos += 1
    fam_doc = templ_doc.EditFamily(i)
    fam_doc.LoadFamily(doc, fm_load_opt())
    echo("Обновлено семейство {}".format(fam_doc.Title), " ", "{}/{}".format(pos, count))

echo(time.time() - start_time)
