# -*- coding: utf-8 -*-
import os, json
from common_scripts import *


class SMemory:
    sd_path = None
    s_path = None
    file_name = None
    memory_file = None
    attributes = None
    is_closed = False

    def __init__(self,script):
        self.s_path = script
        self.sd_path  = os.path.dirname(script)
        if not self.create_conf():
            self.read_conf()
        # echo('Начинаем работу',self.attributes)

    @property
    def script_name(self):
        return os.path.basename(self.s_path)

    @property
    def conf_name(self):
        return self.script_name.split('.')[0]+'.rbm'

    def create_conf(self):
        if not os.path.exists(os.path.join(self.sd_path, self.conf_name)):
            self.memory_file = open(os.path.join(self.sd_path, self.conf_name), 'w')
            self.attributes = {}
            self.memory_file.write(json.dumps(self.attributes))
            self.memory_file.close()
            return True

    def read_conf(self):
        self.memory_file = open(os.path.join(self.sd_path, self.conf_name), 'r')
        text = json.loads(self.memory_file.read())
        # echo(text)
        self.attributes = text

    def SetAttr(self, name, value):
        if not isinstance(value, (float, int, str, bool, list, tuple, dict)):
            value  = to_str(value)
        self.attributes[name] = value

    def GetAttr(self,name):
        name = self.attributes.get(name, 'Not Value')
        if name != 'Not Value':
            return name

    def Close(self):
        #echo('Закончили работу', self.attributes)
        if not self.is_closed:
            self.is_closed = True
            self.memory_file = open(os.path.join(self.sd_path, self.conf_name), 'w')
            self.memory_file.write(json.dumps(self.attributes))
            self.memory_file.close()
        else:
            echo(
'''Вы пытаетесь сохранить память второй раз\n
Если вы работаете c формой - инструкция "MEMORY.Close()" не нужна\n
Если необходимо повторное подключение к памяти - используйте инструкцию "MEMORY = SMemory(FILE)"\n
В конце работы с памятью ее необходимо обязательно закрывать, иначе информация будет утеряна'''
                )
