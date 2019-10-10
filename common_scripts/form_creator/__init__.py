# -*- coding: utf-8 -*-
import clr
clr.AddReference('System.Drawing')
clr.AddReference('System.Windows.Forms')
#

from form_class import Form_creator

def form_start():
    return Form_creator()
