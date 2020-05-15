# -*- coding: utf-8 -*-
from common_scripts import echo
from Autodesk.Revit.DB import FilteredElementCollector, ViewSheet, ParameterFilterElement, View, ViewType, ViewSchedule, ScheduleSheetInstance
from Autodesk.Revit.DB import Viewport, Group
from .Sheet_Complexity import Sheet_Complexity
from .View_Complexity import View_Complexity
from .Scheduled_Complexity import Scheduled_Complexity

# secondary_elements_in_groups найти все элементы не в первой группе и добавить их в этот список. Потом очищать все элементы в группах
# Не забыть про массивы. От них тоже очищать. т.е. за массив давать 1 очко. но не за каждый экземпляр
# Группы тоже очистить

class Project_Complexity:
    all_view = set()

    def __init__(self, doc, analys="document"):
        self.doc = doc
        self.childs = []
        if analys == "document":
            self.view_by_types()
            self.make_schedulde_complex()
            self.make_sheet_complex()
            self.make_schedulde_complex()
            self.make_view_complex()
            self.make_template_complex()
            els = list(self.obj.keys())
            els.sort(reverse=True)
            for i in els:
                echo("{}: {}".format(i, self.obj[i]))

    @property
    def view_ids_in_sheets(self):
        return self._view_ids_in_sheets
    
    @property
    def viewsheets(self):
        if not hasattr(self, "_viewsheets"):
            self._viewsheets = FilteredElementCollector(self.doc).OfClass(ViewSheet).ToElements().Count
        return self._viewsheets

    @property
    def parameter_filter_element(self):
        return FilteredElementCollector(self.doc).OfClass(ParameterFilterElement).GetElementCount()

    @property
    def viewports(self):
        if not hasattr(self, "_viewports"):
            self._viewports = FilteredElementCollector(self.doc).OfClass(Viewport).ToElements()
        return self._viewports.Count
    
    @property
    def schedule_sheet_instances(self):
        if not hasattr(self, "_schedule_sheet_instances"):
            self._schedule_sheet_instances = FilteredElementCollector(self.doc).OfClass(ScheduleSheetInstance).ToElements().Count
        return self._schedule_sheet_instances

    def make_sheet_complex(self):
        self.viewsheets_complex = FilteredElementCollector(self.doc).OfClass(ViewSheet).ToElements()
        self.viewsheets_complex = [Sheet_Complexity(self.doc, i, parent=self) for i in self.viewsheets_complex]

    def make_schedulde_complex(self):
        "Рассчитываем сложность спецификаций."
        self.scheduled_complex = FilteredElementCollector(self.doc).OfClass(ViewSchedule).ToElements()
        self.scheduled_complex = [Scheduled_Complexity(self.doc, i, parent=self) for i in self.scheduled_complex]

    def make_view_complex(self):
        "Рассчитываем сложность видов."
        self.views_complex = [View_Complexity(self.doc, i, parent=self) for i in self.views]
    
    @property
    def groups(self):
        if not hasattr(self, "_groups"):
            self._groups = FilteredElementCollector(self.doc).OfClass(Group).ToElements()
        return self._groups

    @property
    def group_types(self):
        if not hasattr(self, "_group_types"):
            self._group_types = FilteredElementCollector(self.doc).OfClass(define_group_types_and_primary_group).ToElements()
            self._group_types = [i for i in self._group_types if i.Groups.Count]
        return self._group_types

    @property
    def secondary_elements_in_groups(self):
        if not hasattr(self, "_secondary_elements_in_groups"):
            self._secondary_elements_in_groups = List[ElementId]()
            for i in group_types:
                primary = True
                for group in i.Groups:
                    group.GetMemberIds()
                    if not primary:

                    primary = False
        return self._secondary_elements_in_groups
    
    
    def view_by_types(self):
        "Записывает виды по типам."
        all_views = FilteredElementCollector(self.doc).OfClass(View).ToElements()
        all_views = [i for i in all_views if not i.IsTemplate]
        self.views = []
        if not hasattr(self, "_view_3d"):
            self._view_3d = 0
        if not hasattr(self, "_view_drafting"):
            self._view_drafting = 0
        if not hasattr(self, "_view_floor_plan"):
            self._view_floor_plan = 0
        if not hasattr(self, "_view_section"):
            self._view_section = 0
        if not hasattr(self, "_view_area_plan"):
            self._view_area_plan = 0
        if not hasattr(self, "_view_ceiling_plan"):
            self._view_ceiling_plan = 0
        if not hasattr(self, "_view_elevation"):
            self._view_elevation = 0
        if not hasattr(self, "_legend"):
            self._legend = 0
        if not hasattr(self, "_structure_plan"):
            self._structure_plan = 0
        if not hasattr(self, "_detail"):
            self._detail = 0
        if not hasattr(self, "_engineering_plan"):
            self._engineering_plan = 0
        for i in all_views:
            if i.ViewType == ViewType.ThreeD:
                self._view_3d += 1 
                self.views.append(i) 
            elif i.ViewType == ViewType.DraftingView:
                self._view_drafting += 1
                self.views.append(i)  
            elif i.ViewType == ViewType.FloorPlan:
                self._view_floor_plan += 1
                self.views.append(i)  
            elif i.ViewType == ViewType.Section:
                self._view_section += 1
                self.views.append(i)   
            elif i.ViewType == ViewType.AreaPlan:
                self._view_area_plan += 1
                self.views.append(i)   
            elif i.ViewType == ViewType.CeilingPlan:
                self._view_ceiling_plan += 1
                self.views.append(i)   
            elif i.ViewType == ViewType.Elevation:
                self._view_elevation += 1
                self.views.append(i)   
            elif i.ViewType == ViewType.Legend:
                self._legend += 1  
                self.views.append(i) 
            elif i.ViewType == ViewType.Detail:
                self._detail += 1  
                self.views.append(i) 
            elif i.ViewType == ViewType.EngineeringPlan:
                self._engineering_plan += 1 
                self.views.append(i)  

    def make_template_complex(self):
        self.template_complex = FilteredElementCollector(self.doc).OfClass(View).ToElements()
        self.template_complex = [i for i in self.template_complex if i.IsTemplate]


    @property
    def obj(self):
        if not hasattr(self, "_obj"):
            self._obj = {
                "viewsheets": self.viewsheets,
                "parameter_filter_element": self.parameter_filter_element,
                "view_3D": self._view_3d,
                "view_drafting": self._view_drafting,
                "view_floor_plan": self._view_floor_plan,
                "view_section": self._view_section,
                "view_area_plan": self._view_area_plan,
                "view_ceiling_plan": self._view_ceiling_plan,
                "view_elevation": self._view_elevation,
                "view_legend": self._legend,
                "view_detail": self._detail,
                "view_engineering_plan": self._engineering_plan,
                "viewports": self.viewports,
                "scheduleds": len(self.scheduled_complex),
                "templates": len(self.template_complex),
                "schedule_sheet_instances": self.schedule_sheet_instances,
                "groups": self.groups.Count
            }
            for i in self.childs:
                for key, value in i.obj.items():
                    if key == "element_id" or key == "element_name":
                        continue 
                    self._obj.setdefault(key, 0)
                    self._obj[key] += value
        return self._obj