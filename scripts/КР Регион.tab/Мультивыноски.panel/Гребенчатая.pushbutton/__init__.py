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
mark = RB_selections.pick_element_by_class(IndependentTag)
if mark:
    el = doc.GetElement(mark.TaggedElementId.HostElementId).Category
    middle = mark.LeaderElbow
    head = mark.TagHeadPosition
    point = mark.LeaderEnd

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


def get_coordinate():
    uiview = get_active_ui_view(uidoc)
    rect = uiview.GetWindowRectangle()
    p = System.Windows.Forms.Cursor.Position
    dx = float(p.X - rect.Left) / float(rect.Right - rect.Left)
    dy = float(p.Y - rect.Bottom) / float(rect.Top - rect.Bottom)
    v_right = active_view.RightDirection
    v_right = XYZ(fabs(v_right.X), fabs(v_right.Y), fabs(v_right.Z))
    v_up = active_view.UpDirection
    v_up = XYZ(fabs(v_up.X), fabs(v_up.Y), fabs(v_up.Z))
    dxyz = dx * v_right + dy * v_up

    corners = uiview.GetZoomCorners()

    a = corners[0]
    b = corners[1]
    v = b - a

    q = a + dxyz.X * v.X * XYZ.BasisX + dxyz.Y * v.Y * XYZ.BasisY + dxyz.Z * XYZ.BasisZ * v.Z
    return q
def SignedDistanceTo(plane, p):
    v = p - plane.Origin
    return plane.Normal.DotProduct(v)

def project_onto(plane, p):
    d = SignedDistanceTo(plane, p)
    q = p - d * plane.Normal
    return q

if mark:
    plane = Plane.CreateByNormalAndOrigin(active_view.ViewDirection, active_view.Origin)
    middle = project_onto(plane, middle)
    head = project_onto(plane, head)
    point = project_onto(plane, point)

    tagget = True
    while tagget:
        tagget = RB_selections.pick_element_by_category(el)
        if tagget:
            pos = get_coordinate()
            ref = Reference(tagget)
            with Transaction(doc, 'Добавить выноску') as t:
                t.Start()
                vec = (point - middle).Normalize()
                n_pos = project_onto(plane, pos)
                l1 = Line.CreateUnbound(n_pos, vec)
                l2 = Line.CreateUnbound(middle, (head - middle).Normalize())
                inter = StrongBox[IntersectionResultArray]()
                l1.Intersect(l2, inter)
                new_middle = list(inter.Value)[0].XYZPoint
                new_mark = IndependentTag.Create(doc, mark.GetTypeId(), doc.ActiveView.Id, ref, True, mark.TagOrientation, head)
                new_mark.TagHeadPosition  = head
                new_mark.LeaderEndCondition  = mark.LeaderEndCondition
                new_mark.LeaderElbow = new_middle
                # new_pos = pos - middle
                new_mark.LeaderEnd  = pos
                if new_mark.TagText != mark.TagText:
                    doc.Delete(new_mark.Id)
                t.Commit()
