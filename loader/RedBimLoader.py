# -*- coding: utf-8 -*-

import sys
sys.path.append(r'L:\09_Программы\RedBim\loader\scripts')

import os.path as op
# Добавляем адресс

# Запускаем движок
import RedBimEngine

# developer=True
RedBimEngine.find_all_tab(developer=True)
