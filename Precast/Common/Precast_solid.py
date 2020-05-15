# -*- coding: utf-8 -*-
from common_scripts import echo
from Autodesk.Revit.DB import Plane
from Autodesk.Revit.DB import BooleanOperationsUtils, XYZ, PlanarFace
from math import pi
# from common_scripts.line_print import Line_printer


class Precast_solid:
    "Работа с солидами."

    name_parameter = "Мтрл.Название"
    density_parameter = "BDS_Density"
    layer_number_parameter = "BDS_LayerNumber"

    def __init__(self, solid, doc):
        self.doc = doc
        self.element = solid
        self._material_name = None
        self._material = None

    def __repr__(self):
        return "Солид объемом {} {} слой {}".format(self.volume, self.material_name, self.layer_number)

    def get_face_in_point(self, origin=None, normal=None, thick=100 / 304.4):
        # normal = normal.Negate()
        if origin is None:
            origin = self.element.ComputeCentroid()
        sec_plane = Plane.CreateByNormalAndOrigin(normal, origin)
        sol = BooleanOperationsUtils.CutWithHalfSpace(self.element, sec_plane)
        vert_vect = XYZ(0,0,1)
        if not normal.IsAlmostEqualTo(vert_vect) and not normal.IsAlmostEqualTo(vert_vect.Negate()):
            origin += normal * (thick / 2)
            normal = normal.Negate()
            sec_plane = Plane.CreateByNormalAndOrigin(normal, origin)
            sol = BooleanOperationsUtils.CutWithHalfSpace(sol, sec_plane)
        faces = []
        if sol:
            for face in sol.Faces:
                if isinstance(face, PlanarFace):
                    # angle = face.FaceNormal.AngleTo(normal)
                    # if angle < pi / 2.1 or angle > pi * 1.6:
                    faces.append(face)
            return faces

    @property
    def volume(self):
        return self.element.Volume * 0.02832

    @property
    def mass(self):
        if self.material_density:
            return self.volume * self.material_density
        return 0

    @property
    def material(self):
        if self._material is None:
            if self.element.Faces.Size:
                self._material = self.doc.GetElement(self.element.Faces.Item[0].MaterialElementId)
        return self._material

    @property
    def layer_number(self):
        if self.material:
            par = self.material.LookupParameter(self.layer_number_parameter)
            if par:
                return par.AsInteger()

    @property
    def material_name(self):
        if self._material_name is None:
            if self.material:
                    self._material_name = self.material.GetParameters(self.name_parameter)[0].AsString()
        return self._material_name

    @property
    def material_density(self):
        if self.material:
            r = self.material.GetParameters(self.density_parameter)[0]
            if not r.AsString():
                r = r.AsDouble()
            else:
                r = r.AsString()
            if r:
                return float(r)

