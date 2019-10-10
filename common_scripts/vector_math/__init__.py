# coding: utf8
from math import sin, cos, radians
from Autodesk.Revit.DB import XYZ


def XYZ_multiply(a, b):
    """Выполняет векторное перемнодение двух векторов."""
    new_x = a.Y * b.Z - a.Z * b.Y
    new_y = a.Z * b.X - a.X * b.Z
    new_z = a.X * b.Y - a.Y * b.X
    return XYZ(new_x, new_y, new_z).Normalize()


def rotate_point_by_axec(xyz, deg, axe='z'):
    sint = sin(radians(deg))
    cost = cos(radians(deg))
    if axe == "z":
        x = xyz.X * cost - xyz.Y * sint
        y = xyz.X * sint + xyz.Y * cost
    return XYZ(x, y, xyz.Z)
