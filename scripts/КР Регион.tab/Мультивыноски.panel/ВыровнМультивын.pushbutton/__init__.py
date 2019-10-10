import re
import sys
from clr import StrongBox
from System.Collections.Generic import IList
from math import fabs
import System.Windows.Forms
from Autodesk.Revit.DB import Dimension, Transaction, XYZ, BuiltInCategory
from Autodesk.Revit.DB import Reference, IndependentTag, Transform, Line
from Autodesk.Revit.DB import IntersectionResultArray, Plane
from Autodesk.Revit.DB import ClosestPointsPairBetweenTwoCurves
from common_scripts.get_elems.RB_selections import RB_selections
uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document
active_view = doc.ActiveView

def vect_cur_view(view):
    v_right = active_view.RightDirection
    v_right = XYZ(fabs(v_right.X), fabs(v_right.Y), fabs(v_right.Z))
    v_up = active_view.UpDirection
    v_up = XYZ(fabs(v_up.X), fabs(v_up.Y), fabs(v_up.Z))
    return (v_right + v_up)

def get_active_ui_view(uidoc):
    doc = uidoc.Document
    view = doc.ActiveView
    uiviews = uidoc.GetOpenUIViews()
    uiview = None
    for uv in uiviews:
        if uv.ViewId.Equals(view.Id):
            uiview = uv
            break
    return uiview

def SignedDistanceTo(plane, p):
    v = p - plane.Origin
    return plane.Normal.DotProduct(v)

def project_onto(plane, p):
    d = SignedDistanceTo(plane, p)
    q = p - d * plane.Normal
    return q

general_mark = RB_selections.pick_element_by_class(IndependentTag)
taggets = RB_selections.pick_elements_by_class(IndependentTag)
if taggets and general_mark:
    plane = Plane.CreateByNormalAndOrigin(active_view.ViewDirection, active_view.Origin)

    middle = project_onto(plane, general_mark.LeaderElbow)
    head = project_onto(plane, general_mark.TagHeadPosition)
    point = project_onto(plane, general_mark.LeaderEnd)

    vect = (point - middle).Normalize()
    l1 = Line.CreateUnbound(head, (middle - head).Normalize())
    with Transaction(doc, "Выровнять марки") as t:
        t.Start()
        for i in taggets:
            tag_point = project_onto(plane, i.LeaderEnd)
            l2 = Line.CreateUnbound(tag_point, vect)
            inter = StrongBox[IntersectionResultArray]()
            l1.Intersect(l2, inter)
            new_middle = list(inter.Value)[0].XYZPoint
            i.LeaderElbow = new_middle
            i.TagHeadPosition = head
        t.Commit()