import re
import sys
from math import fabs
import System.Windows.Forms
from Autodesk.Revit.DB import Dimension, Transaction, XYZ, BuiltInCategory
from Autodesk.Revit.DB import Reference, IndependentTag, Transform

from common_scripts.get_elems.RB_selections import RB_selections
uidoc = __revit__.ActiveUIDocument
doc = uidoc.Document
active_view = doc.ActiveView
mark = RB_selections.pick_element_by_class(IndependentTag)
if mark:
    el = doc.GetElement(mark.TaggedElementId.HostElementId).Category
    
    head = mark.TagHeadPosition
    point = mark.LeaderEnd
    if not mark.HasElbow:
        message("Нарисуйте марку так, чтобы промежуточное звено было за последним стержнем маркировки")
        mark = None
    middle = mark.LeaderElbow

def vect_cur_view(view):
    v_right = active_view.RightDirection
    v_right = XYZ(fabs(v_right.X), fabs(v_right.Y), fabs(v_right.Z))
    v_up = active_view.UpDirection
    v_up = XYZ(fabs(v_up.X), fabs(v_up.Y), fabs(v_up.Z))
    return v_right + v_up

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
if mark:
    tagget = True
    p_v = (point - middle).Normalize()
    p_v = XYZ(fabs(p_v.X), fabs(p_v.Y), fabs(p_v.Z))

    while tagget:
        tagget = RB_selections.pick_element_by_category(el)
        if tagget:
            pos = get_coordinate()
            ref = Reference(tagget)
            with Transaction(doc, 'Добавить выноску') as t:
                t.Start()
                new_mark = IndependentTag.Create(doc, mark.GetTypeId(), doc.ActiveView.Id, ref, True, mark.TagOrientation, pos)
                new_mark.TagHeadPosition  = head
                new_mark.LeaderEndCondition  = mark.LeaderEndCondition
                distance = (pos - middle).GetLength()
                new_mark.LeaderElbow = middle
                new_pos = pos - middle
                new_mark.LeaderEnd  = middle + XYZ(new_pos.X * p_v.X, new_pos.Y * p_v.Y, new_pos.Z * p_v.Z)
                if new_mark.TagText != mark.TagText:
                    doc.Delete(new_mark.Id)
                t.Commit()
