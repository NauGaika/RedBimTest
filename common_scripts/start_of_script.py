# -*- coding: utf-8 -*-
import clr, sys, os
sys.path.append('L:\\09_Программы\\RedBim\\loader')
clr.AddReference('IronPython.SQLite')
clr.AddReference('System')
clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Drawing')
clr.AddReference('System.Web')
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
sys.path.append('L:\\09_Программы\\RedBim')
sys.path.append('L:\\09_Программы\\RedBim\\')

# import sqlite3
from common_scripts import *
from common_scripts.script_memory import SMemory
from common_scripts.form_creator import form_start

# db_path = "L:\\02_Revit\\18_Обучение BIM\\Обучение_КР\\RedBim\\RedBimStatistic.db"

file_path = os.path.dirname(FILE)
sys.path.append(file_path)
file_name = os.path.basename(file_path)
# conn = sqlite3.connect(db_path)
# cursor = conn.cursor()

# sql = """
# INSERT INTO plagin_access(plagin, user, path) VALUES(?, ?, ?)
# """

# cursor.execute(sql, (file_name, __revit__.Application.Username, file_path))
# conn.commit()
# conn.close()
#MEMORY = SMemory(FILE)
FORM = form_start()
#
#
#
#
#
#