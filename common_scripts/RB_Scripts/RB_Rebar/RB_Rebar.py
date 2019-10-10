# coding: utf8
"""Пакет скриптов по работе с арматурой"""
from Autodesk.Revit.DB.Structure import Rebar, RebarHookOrientation, RebarLayoutRule
from Autodesk.Revit.DB import ElementTransformUtils

from Autodesk.Revit.DB.ElementTransformUtils import MoveElement
from common_scripts import echo
doc = __revit__.ActiveUIDocument.Document


class RB_Rebar:
    """Класс арматуры."""
    @property
    def ArrayLength(self):
        return self.rebar.GetShapeDrivenAccessor().ArrayLength

    @property
    def Normal(self):
        return self.rebar.GetShapeDrivenAccessor().Normal

    def __init__(self,rebar):
        """Инициализация объекта арматуры."""
        self.rebar = rebar

    def SetMaximumSpacing(self, space, distance, first=True, last=True, in_normal_side=True):
        """Арматура с максимальным расстоянием."""
        self.rebar.GetShapeDrivenAccessor().SetLayoutAsMaximumSpacing(space,
                                                                      distance,
                                                                      in_normal_side,
                                                                      first,
                                                                      last)

    def SetAsNumberWithSpacing(self, count, space, first=True, last=True):
        """Устанавливаем количесвто с шагом"""
        self.rebar.GetShapeDrivenAccessor().SetLayoutAsNumberWithSpacing(count, space, True, first, last)

    def SetAsSingle(self):
        """Устанавливаем как один."""
        self.rebar.GetShapeDrivenAccessor().SetLayoutAsSingle()

    def copy_by_normal_length(self, vect):
        """Копировать арматуру по вектору"""
        return self.__class__(doc.GetElement(ElementTransformUtils.CopyElement(doc, self.rebar.Id, vect)[0]))

    def translate(self, vect):
        MoveElement(doc, self.rebar.Id, vect)
    @classmethod
    def create_rebar(cls, shape, rebar_shape, rebar_type, host, direction):
        """Создание арматуры по форме."""
        self.rebar = Rebar.CreateFromCurvesAndShape(doc,
                                              rebar_shape,
                                              rebar_type,
                                              None,
                                              None,
                                              host,
                                              direction,
                                              shape,
                                              RebarHookOrientation.Right,
                                              RebarHookOrientation.Right
                                              )
        return self

    def set_rebar_space(self, start_space, end_space):
        if self.rebar.LayoutRule == RebarLayoutRule.MaximumSpacing:
            self.translate(self.Normal*start_space)
            self.rebar.GetShapeDrivenAccessor().ArrayLength = self.ArrayLength - start_space - end_space
