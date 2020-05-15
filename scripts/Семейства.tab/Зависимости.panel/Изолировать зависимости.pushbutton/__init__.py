
# import os
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, FamilyInstance, Transaction
from Autodesk.Revit.DB import Extrusion, Sweep, Dimension, ElementId, ReferencePlane

# from Autodesk.Revit.UI.Selection import SelElementSet

from System.Collections.Generic import List

doc = __revit__.ActiveUIDocument.Document
selection = [doc.GetElement(elId) for elId in __revit__.ActiveUIDocument.Selection.GetElementIds()]

class Depend:
    _references = None

    def __init__(self, el):
        self.el = el
        self.select_depends()

    @property
    def lines(self):
        lines = []
        if isinstance(self.el, Extrusion):
            for i in self.el.Sketch.Profile:
                lines += [c.Reference.ElementId for c in list(i)]
        if isinstance(self.el, Sweep):
            for i in self.el.PathSketch.Profile:
                lines += [c.Reference.ElementId for c in list(i)]
            for i in self.el.ProfileSketch.Profile:
                lines += [c.Reference.ElementId for c in list(i)]
        if isinstance(self.el, FamilyInstance):
            lines = [self.el.Id]
        if isinstance(self.el, ReferencePlane):
            lines = [self.el.Id]
        if isinstance(self.el, Dimension):
            for i in self.el.References:
                lines.append(i.ElementId)
        return lines

    @property
    def dimensions(self):
        return FilteredElementCollector(doc).OfClass(Dimension).ToElements()

    @property
    def references(self):
        if self.__class__._references is None:
            references = {}
            for dim in self.dimensions:
                for ref in dim.References:
                    references.setdefault(ref.ElementId, [])
                    references[ref.ElementId].append(dim)
            self.__class__._references = references
        return self.__class__._references

    def select_depends(self):
        self.lines
        if (isinstance(self.el, Dimension)):
            result = [self.el.Id]
            for i in self.el.References:
                result.append(i.ElementId)
        else:
            result = [self.el.Id]
        self.select_depend(self.lines, step=1, result=result)
        result = list(set(result))
        new_arr = List[ElementId](result)
        t = Transaction(doc, "sd")
        t.Start()
        __revit__.ActiveUIDocument.Selection.SetElementIds(new_arr)
        doc.ActiveView.IsolateElementsTemporary(new_arr)
        t.Commit()

    def select_depend(self, elids, step=1, result=None):
        step -= 1
        res = []
        dim = []
        for i in elids:
            if i in self.references.keys():
                res += self.references[i]
                dim += [j.Id for j in self.references[i]]
        new_res = []
        for j in res:
            for k in j.References:
                new_res.append(k.ElementId)
        result += new_res + dim
        if step:
            self.select_depend(new_res, step=step, result=result)

Depend(selection[0])