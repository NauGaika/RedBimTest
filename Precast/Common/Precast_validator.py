# -*- coding: utf-8 -*-
# from common_scripts import echo


class Precast_validator(object):
    def __init__(self):
        "Инит для валидаторов."
        if hasattr(self, "analys_geometry") and self.analys_geometry:
            self.element_error = ""
            self.status = ""
        super(Precast_validator, self).__init__()

    @property
    def is_valid(self):
        return True

    @property
    def element_error(self):
        par = self.element.LookupParameter("Error")
        if par:
            res = par.AsString()
            if res:
                return par.AsString()
        return ""

    @element_error.setter
    def element_error(self, val):
        par = self.element.LookupParameter("Error")
        if par:
            par.Set(val)
        if hasattr(self, "parent") and hasattr(self.parent, "error"):
            self.parent.element_error = val

    @property
    def status(self):
        par = self.element.LookupParameter("Status")
        if par:
            res = par.AsString()
            if res:
                return par.AsString()
        return ""

    @status.setter
    def status(self, val):
        par = self.element.LookupParameter("Status")
        if par:
            par.Set(val)
        if hasattr(self, "parent") and hasattr(self.parent, "Status"):
            self.parent.status = val