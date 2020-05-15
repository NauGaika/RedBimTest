# -*- coding: utf-8 -*-
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory
from Autodesk.Revit.DB import ViewType, Dimension, IndependentTag, CurveElement, DetailLine, TextNote, ElementId, ViewDetailLevel
from common_scripts import echo


class View_Complexity:
    def __init__(self, doc, view, parent=None):
        self.doc = doc
        self.view = view
        self.parent = parent
        self.childs = []
        if self.parent:
            self.parent.childs.append(self)

    @property
    def text_notes(self):
        if not hasattr(self, "_text_notes"):
            self._text_notes = FilteredElementCollector(self.doc, self.view.Id).OfClass(TextNote).ToElementIds().Count
        return self._text_notes

    @property
    def annotation_symbol(self):
        if not hasattr(self, "_annotation_symbol"):
            if self.view.ViewType == ViewType.ThreeD:
                self._annotation_symbol = 0
            else:
                self._annotation_symbol = FilteredElementCollector(self.doc, self.view.Id).OfCategory(BuiltInCategory.OST_GenericAnnotation).ToElementIds().Count
        return self._annotation_symbol

    @property
    def dimension_segments(self):
        if not hasattr(self, "_dimension_segments"):
            dims = FilteredElementCollector(self.doc, self.view.Id).OfClass(Dimension).ToElements()
            self._dimension_segments = 0
            for dim in dims:
                if dim.Segments:
                    self._dimension_segments += len(list(dim.Segments))
                else:
                    self._dimension_segments += 1
        return self._dimension_segments

    @property
    def independent_tag(self):
        if not hasattr(self, "_independent_tag"):
            self._independent_tag = FilteredElementCollector(self.doc, self.view.Id).OfClass(IndependentTag).ToElements().Count
        return self._independent_tag

    @property
    def detail_lines(self):
        if not hasattr(self, "_detail_lines"):
            self._detail_lines = FilteredElementCollector(self.doc, self.view.Id).OfClass(CurveElement).ToElements()
            self._detail_lines = len([i for i in self._detail_lines if isinstance(i, DetailLine)])
        return self._detail_lines

    @property
    def detail_components(self):
        if not hasattr(self, "_detail_components"):
            self._detail_components = FilteredElementCollector(self.doc, self.view.Id).OfCategory(BuiltInCategory.OST_DetailComponents).ToElements().Count
        return self._detail_components
    
    @property
    def view_with_template(self):
        if self.view.ViewTemplateId:
            return 1
        return 0
    
    @property
    def applied_filters(self):
        if self.view.ViewTemplateId != ElementId.InvalidElementId:
            return 0
        return self.view.GetFilters().Count
    
    @property
    def view_category_overrides(self):
        if self.view.ViewTemplateId != ElementId.InvalidElementId:
            return 0
        res = 0
        for i in self.doc.Settings.Categories:
            over = self.view.GetCategoryOverrides(i.Id)
            if over.CutBackgroundPatternColor.IsValid:
                res += 1
            elif over.CutBackgroundPatternId != ElementId.InvalidElementId:
                res += 1
            elif over.CutForegroundPatternColor.IsValid:
                res += 1
            elif over.CutForegroundPatternId != ElementId.InvalidElementId:
                res += 1
            elif over.CutLineColor.IsValid:
                res += 1
            elif over.CutLinePatternId != ElementId.InvalidElementId:
                res += 1
            elif over.CutLineWeight != -1:
                res += 1
            elif over.DetailLevel != ViewDetailLevel.Undefined:
                res += 1
            elif over.Halftone:
                res += 1
            elif not over.IsCutBackgroundPatternVisible:
                res += 1
            elif not over.IsCutForegroundPatternVisible:
                res += 1
            elif not over.IsSurfaceBackgroundPatternVisible:
                res += 1
            elif not over.IsSurfaceForegroundPatternVisible:
                res += 1
            elif over.ProjectionLineColor.IsValid:
                res += 1
            elif over.ProjectionLinePatternId != ElementId.InvalidElementId:
                res += 1
            elif over.SurfaceBackgroundPatternColor.IsValid:
                res += 1
            elif over.SurfaceBackgroundPatternId != ElementId.InvalidElementId:
                res += 1
            elif over.SurfaceForegroundPatternId != ElementId.InvalidElementId:
                res += 1
            elif over.SurfaceForegroundPatternColor.IsValid:
                res += 1
            elif over.ProjectionLineWeight != -1:
                res += 1
        return res

    @property
    def obj(self):
        res = {
            "element_id": str(self.view.Id.IntegerValue),
            "element_name": self.view.Title,
            "annotation_symbols": self.annotation_symbol,
            "dimension_segments": self.dimension_segments,
            "independent_tag": self.independent_tag,
            "text_notes_on_view": self.text_notes,
            "detail_lines_on_view":self.detail_lines,
            "detail_components": self.detail_components,
            "view_with_template": self.view_with_template,
            "applied_filters_to_view": self.applied_filters,
            "view_category_overrides": self.view_category_overrides
            }
        for i in self.childs:
            for key, value in i.items():
                if key == "element_id" or key == "element_name":
                    continue 
                res.setdefault(key, 0)
                res[key] += value
        return res