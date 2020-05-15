import re
import sys
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
    middle = mark.LeaderElbow
    head = mark.TagHeadPosition
    point = mark.LeaderEnd


    taggets = RB_selections.pick_elements_by_class(IndependentTag)
    with Transaction(doc, "Выровнять марки") as t:
        t.Start()
        for tag in taggets:
            tag.TagHeadPosition = head
            tag.LeaderElbow = middle
        t.Commit()
