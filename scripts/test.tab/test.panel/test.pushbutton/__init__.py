# coding: utf8
"""Добавляем необходимые фильтры для КЖ"""
import os
# import re
# from math import pi
# from Autodesk.Revit.DB import Transaction, ElementId, FilteredElementCollector, ParameterFilterElement, LogicalAndFilter, \
#                             LogicalOrFilter, ElementParameterFilter, ElementFilter, FilterRule, FilterStringRule, FilterInverseRule
# from Autodesk.Revit.DB.Structure import RebarInSystem, Rebar
# from System.Collections.Generic import List


uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
curview = uidoc.ActiveGraphicalView
selection = [doc.GetElement(elId) for elId in __revit__.ActiveUIDocument.Selection.GetElementIds()]

start_path = "G:\\Мой диск\\_СТК"
file = None

def get_all_files(path, c=0):
	for i in os.listdir(path):
		new_path = os.path.join(path, i)
		if os.path.isdir(new_path):
			get_all_files(new_path, c=c)
		if os.path.isfile(new_path):
			if os.path.isfile(new_path) and new_path[-4:] == '.rvt':
				if c< 2:
					message(new_path)
					new_file = __revit__.OpenAndActivateDocument(new_path)
					if file:
						file = file.Close(True)
					file = new_file
					c+=1

get_all_files(start_path)