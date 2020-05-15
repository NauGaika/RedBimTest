from Autodesk.Revit.DB import Transaction, FilteredElementCollector, \
BuiltInCategory, ElementId, IFamilyLoadOptions, FamilySource, \
Plane, XYZ, SketchPlane, Line, ViewSection, ViewSheet
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
        bool_.Value = True
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

def foo(doc):
    try:
        with Transaction(doc, "Временная линия") as t:
            t.Start()
            creDoc = doc.FamilyCreate
            # ff = FilteredElementCollector(doc).OfClass(ViewSection)
            # ff.UnionWith(FilteredElementCollector(doc).OfClass(ViewSheet))
            # view = ff.FirstElement()
            try:
                plane = Plane.CreateByThreePoints(XYZ(0,0,0), XYZ(0,1,0), XYZ(1,0,0))
                new_line = Line.CreateBound(XYZ(0,0,0), XYZ(0,1,0))
                sketchPlane = SketchPlane.Create(doc, plane)
                new_line = creDoc.NewSymbolicCurve(new_line, sketchPlane)
            except:
                ff = FilteredElementCollector(doc).OfClass(ViewSection)
                ff.UnionWith(FilteredElementCollector(doc).OfClass(ViewSheet))
                view = ff.FirstElement()
                new_line = Line.CreateBound(view.Origin, view.Origin + view.RightDirection)
                new_line = creDoc.NewDetailCurve(view, new_line)
            t.Commit()
            with Transaction(doc, "Удаляю") as t2:
                t2.Start()
                doc.Delete(new_line.Id)
                t2.Commit()
            return True
    except:
        pass
        # echo("Все посыпалось на ", doc.Title)

for i in els:
    pos += 1
    fam_doc = templ_doc.EditFamily(i)
    res = foo(fam_doc)
    if res:
        fam_doc.LoadFamily(doc, fm_load_opt())
        echo("Обновлено семейство {}".format(fam_doc.Title), " ", "{}/{}".format(pos, count))
    else:
        echo("Не обновлено семейство {}".format(fam_doc.Title), " ", "{}/{}".format(pos, count))
    fam_doc.Close(False)

echo(time.time() - start_time)
