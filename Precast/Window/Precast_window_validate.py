# -*- coding: utf-8 -*-
from common_scripts import echo


class Precast_window_validate(object):
    def __init__(self):
        super(Precast_window_validate, self).__init__()

    @property
    def modul_tiles_width(self):
        return 150

    @property
    def modul_seam_width(self):
        return 15

    @property
    def is_valid(self):
        if not hasattr(self, "_is_valid"):
            for i in self.children:
                if not i.is_valid:
                    self._is_valid = False
                    break
            else:
                point = self.make_real_point()
                x1 = round(point.X * 304.8, 5)
                x2 = round((self.parent.length * 304.8 - 15) -
                           x1 - self.width * 304.8, 5)
                res1 = round((x1 + self.modul_seam_width),
                             1) % self.modul_tiles_width
                res2 = round((x2 + self.modul_seam_width),
                             1) % self.modul_tiles_width
                if not (res1 == 0 or res2 == 0):
                    msg = "Не верное размещение окна по ширине. {}".format(
                        self)
                    echo(msg)
                    self.element_error = msg
                    self._is_valid = False
                else:
                    self._is_valid = True
        return self._is_valid
