
# import os
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, Transaction, SharedParameterElement, ParameterElement, ParameterType
import random

doc = __revit__.ActiveUIDocument.Document

class Crash_test:
    "Рандомное заполнение параметров семейства."
    
    def __init__(self):
        self.fm = doc.FamilyManager
        self._all_parameters = None
        self.randomize_parameters()

    @property
    def all_parameters(self):
        if self._all_parameters is None:
            self._all_parameters = self.fm.GetParameters()
            res = []
            for i in self._all_parameters:
                if i.IsReadOnly:
                    continue
                if i.IsDeterminedByFormula:
                    continue
                if i.UserModifiable:
                    continue
                par_type = i.Definition.ParameterType
                
                if par_type == ParameterType.Integer or par_type == ParameterType.Number or par_type == ParameterType.Length or par_type == ParameterType.Angle or par_type == ParameterType.Currency:
                    if self.get_parameter_value(i):
                        res.append(i)
            self._all_parameters = res
        return self._all_parameters
    
    def randomize_parameters(self, randomize=1):
        with Transaction(doc, "Рандомные параметры") as t:
            t.Start()
            for i in self.all_parameters:
                val = self.get_parameter_value(i)
                set_val = random.uniform(val * -1, val)
                if i.Definition.ParameterType == ParameterType.Length:
                    val /= 304.8
                    set_val /= 304.8
                self.fm.Set(i, val + set_val)
            t.Commit()
            
            
            
    def get_parameter_value(self, parameter):
        fam_type = list(self.fm.Types)[0]
        val = fam_type.AsValueString(parameter)
        if val:
            return float(val)

if doc.IsFamilyDocument:
    Crash_test()
    
    14119744