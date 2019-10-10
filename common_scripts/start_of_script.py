# -*- coding: utf-8 -*-
import clr, sys, os
clr.AddReference('System')
clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Drawing')
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
sys.path.append('\\\\picompany.ru\\pikp\\Dep\\LKP4\\WORK\\scripts')

from common_scripts import *
from common_scripts.script_memory import SMemory
from common_scripts.form_creator import form_start
from common_scripts.get_elems import get_elem_by_click

#MEMORY = SMemory(FILE)
FORM = form_start()
#
