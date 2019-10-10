# coding: utf8
from common_scripts import echo
from math import pi
from Autodesk.Revit.DB import XYZ, Line, Arc, SketchPlane, Plane, UV, GraphicsStyle, FilteredElementCollector
from common_scripts.vector_math import XYZ_multiply

class Line_printer:
    @classmethod
    def get_line_style(cls, color='еленая'):
        """Получаем стиль линии."""
        doc = __revit__.ActiveUIDocument.Document
        els = FilteredElementCollector(doc).OfClass(GraphicsStyle).ToElements()
        for i in els:
            if color in i.Name:
                return i

    @classmethod
    def print_curve_loop(cls, cl):
        for elem in cl:
            if isinstance(elem, Line):
                cls.print_arc(elem.GetEndPoint(0), cl.GetPlane())
                cls.print_line(elem.GetEndPoint(0), elem.GetEndPoint(1),
                               cl.GetPlane())
        # for
        # cls.print_arc(, cl.GetPlane())

    @classmethod
    def print_line(cls, p1, p2, plane=None, radius=0.3, color='еленая'):
        doc = __revit__.ActiveUIDocument.Document
        active_view = doc.ActiveView
        creDoc = __revit__.ActiveUIDocument.Document.Create
        if not plane:
            vect = p2 - p1
            p3 = p1 + XYZ_multiply(active_view.ViewDirection, vect).Normalize()
            plane = Plane.CreateByThreePoints(p1, p2, p3)
        sketchPlane = SketchPlane.Create(doc, plane)
        new_line = Line.CreateBound(p1, p2)
        m_line = creDoc.NewModelCurve(
            new_line,
            sketchPlane
        )
        m_line.LineStyle = cls.get_line_style(color=color)
        return m_line

    @classmethod
    def print_arc(cls, point, plane=None, radius=0.3):
        doc = __revit__.ActiveUIDocument.Document
        active_view = doc.ActiveView
        creDoc = __revit__.ActiveUIDocument.Document.Create
        if not plane:
            plane = Plane.CreateByNormalAndOrigin(active_view.ViewDirection, point)
        sketchPlane = SketchPlane.Create(doc, plane)
        new_arc = Arc.Create(point,
                             radius,
                             0,
                             pi * 2,
                             plane.XVec,
                             plane.YVec)
        m_line = creDoc.NewModelCurve(
            new_arc,
            sketchPlane
        )
        return m_line

    @classmethod
    def print_curve(cls, curve, color):
        doc = __revit__.ActiveUIDocument.Document
        active_view = doc.ActiveView
        creDoc = __revit__.ActiveUIDocument.Document.Create
        cls.print_line(curve.GetEndPoint(0), curve.GetEndPoint(1))

    @classmethod
    def print_region(cls, region, color='еленая', protect=False):
        if protect:
            tl, tr, br, bl = region.protect_corners
        else:
            tl, tr, br, bl = region.to_xyz(region.corners)
        cls.print_line(tr, bl, color=color)
        cls.print_line(tl, br, color=color)
        cls.print_line(tr, tl, color=color)
        cls.print_line(tl, bl, color=color)
        cls.print_line(bl, br, color=color)
        cls.print_line(br, tr, color=color)

        # sketchPlane
