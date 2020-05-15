# -*- coding: utf-8 -*-
# from common_scripts import echo


class Precast_panel_validate(object):
    def __init__(self):
        "Инит в тором производится валидация панели."
        # self.error = ""
        super(Precast_panel_validate, self).__init__()

    @property
    def is_valid(self):
        if not hasattr(self, "_is_valid"):
            for i in self.children:
                if not i.is_valid:
                    self._is_valid = False
                    break
            else:
                self._is_valid = True
        return self._is_valid
