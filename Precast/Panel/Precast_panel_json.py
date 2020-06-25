# -*- coding: utf-8 -*-
from clr import StrongBox
from Autodesk.Revit.DB import BoundingBoxIntersectsFilter, FilteredElementCollector, Outline, FamilyInstance
from Autodesk.Revit.DB import BooleanOperationsUtils, BooleanOperationsType, SetComparisonResult, IntersectionResultArray, BoundingBoxIsInsideFilter
from Autodesk.Revit.DB import Line, SolidCurveIntersectionOptions, XYZ, CurveLoop, BuiltInCategory, ElementId

from common_scripts import echo
from System.Collections.Generic import List


class Precast_panel_json(object):
    @property
    def json(self):
        if not hasattr(self, "_json"):
            echo(self)
            echo("Состоит из:")
            res_obj = [{
                "point": self.make_xyz(XYZ()),
                "type": "Body",
                "solids": []
            }]

            for key in self.plan.keys():
                obj = {
                    "layer": key,
                    "cutting": False,
                    "plan": [self.make_xyz(i, nullable_z=True) for i in self.plan[key]["points"]],
                    "profile": [self.make_xyz(i, nullable_x=True) for i in self.profile[key]["points"]],
                    "point": self.make_xyz(XYZ(self.plan[key]["point"].X, self.plan[key]["point"].Y, self.profile[key]["point"].Z)),
                }
                res_obj[0]["solids"].append(obj)

            for i in self.holes:
                res_obj.append(i.define_json())
            # echo(self.mark_prefix_param)
            # self.facade_type_param = self.facade_type_param if self.facade_type_param else ""
            res_obj = {
                "series": self.series_param,
                "markPrefix": self.mark_prefix_param + self.facade_type_param,
                "markSubPrefix": self.mark_sub_prefix_param,
                "constructionType": self.construction_type_param,
                "handle": self.element.Id.IntegerValue,
                "components": {
                    "componentVals": res_obj,
                    "componentRefs": []
                },
                "details": []
            }

            for i in self.windows:
                echo(i, "", i.mesure)
                res_obj["components"]["componentRefs"].append(i.define_json())

            for i in res_obj["components"]["componentVals"]:
                i["solids"].sort(key=lambda x: x['layer'])
            # sel = __revit__.ActiveUIDocument.Selection
            # els = List[ElementId]()
            for i in self.embedded_parts:
                # els.Add(i.element.Id)
                echo(i.tag, " ", i.mesure, " ", i.Id)
                res_obj["details"].append(i.define_json())
            # sel.SetElementIds(els)
            self._json = res_obj
            echo("  ")
        return self._json
