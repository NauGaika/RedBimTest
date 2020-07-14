# -*- coding: utf-8 -*-
"""Модуль который ищет вкладки. Здесь функция find_all_tab."""

import os
import re

from constants import DIR_SCRIPTS, DIR_SYSTEM_SCRIPTS  # Подгружаем общие переменные
from common_scripts import echo, message
from RB_Tab_class import RB_Tab  # Подгружаем класс с вкладками

import os
import json
from System.Windows.Forms import MessageBox, Application, Form, DockStyle, BorderStyle, TextBox, ScrollBars, AnchorStyles, AutoScaleMode
from System.Windows.Forms import ImageLayout, FormStartPosition, Label, TreeView, Button
from System.Windows.Forms import TreeNode, TreeViewAction
from System.Web.UI.WebControls import TreeNodeTypes
from System.Drawing import Font, FontStyle, Color, Point, Image, Icon

prev_path = ""
SCRIPTS_PATH = __file__
while "RedBim" != prev_path and "RedBimTest" != prev_path:
    SCRIPTS_PATH = os.path.abspath(os.path.dirname(SCRIPTS_PATH))
    prev_path = os.path.split(SCRIPTS_PATH)[-1]
    # message(prev_path)
STATIC_IMAGE = os.path.join(SCRIPTS_PATH, 'static\\img')
SCRIPTS_PATH = os.path.join(SCRIPTS_PATH, 'scripts')


class RB_TreeView(TreeView):
    def __init__(self):
        self.AfterCheck += self.node_AfterCheck

    def node_AfterCheck(self, sender, e):
        if e.Action != TreeViewAction.Unknown:
            self.CheckAllParentNodes(e.Node, e.Node.Checked)
            if e.Node.Nodes.Count > 0:
                self.CheckAllChildNodes(e.Node, e.Node.Checked)

    def CheckAllChildNodes(self,treeNode, nodeChecked):
        
        for node in treeNode.Nodes:
            node.Checked = nodeChecked
            if node.Nodes.Count > 0:
                self.CheckAllChildNodes(node, nodeChecked)

    def CheckAllParentNodes(self, treeNode, nodeChecked):
        if hasattr(treeNode, "Parent"):
            if treeNode.Parent:
                if nodeChecked:
                    treeNode.Parent.Checked = nodeChecked
                    self.CheckAllParentNodes(treeNode.Parent, nodeChecked)

class RedBimSetting(Form):
    def __init__(self):
        self.pushbutons = []

        self.Text = 'RedBim набор плагинов'
        self.Name = 'RedBimSetting'
        self.Height = 450
        self.Width = 400
        self.AutoScroll = True
        self.AutoScaleMode = AutoScaleMode.Font
        self.BackColor = Color.FromArgb(67, 67, 67)
        # self.BackgroundImage = Image.FromFile(os.path.join(STATIC_IMAGE, "bg.png"))
        # self.BackgroundImageLayout = ImageLayout.Center
        self.Icon = Icon(os.path.join(STATIC_IMAGE, "icon.ico"), 16, 16)
        self.StartPosition = FormStartPosition.CenterScreen
        self.tree = RB_TreeView()
        self.tree.CollapseAll()
        self.tree.BackColor = Color.FromArgb(67, 67, 67)
        self.tree.BackgroundImage = Image.FromFile(os.path.join(STATIC_IMAGE, "bg.png"))
        self.tree.BackgroundImageLayout = ImageLayout.Center
        self.tree.Font = Font("ISOCPEUR", 12, FontStyle.Italic)
        self.tree.ForeColor = Color.White
        self.tree.CheckBoxes = True
        self.tree.Height = 378
        self.tree.Dock = DockStyle.Top
        self.find_all_pushbuttons()
        self.button = Button()
        self.button.Dock = DockStyle.Bottom
        self.button.Text = "Сохранить настройки"
        self.button.Height = 32
        self.button.Font = Font("ISOCPEUR", 12, FontStyle.Italic)
        self.button.ForeColor = Color.White
        self.button.BackColor = Color.Green
        self.button.Click += self.active_button

        self.Controls.Add(self.button)
        self.Controls.Add(self.tree)

    def find_element(self, path, element, parent=None):
        # message("Ищу скрипты в {}".format(path))
        ress = []
        for i in os.listdir(path):
            if i[len(element) * -1:] == element:
                result = {}
                result.setdefault("path", os.path.join(path, i))
                result.setdefault("element_type", element[1:])
                result.setdefault("name", i)
                result.setdefault("parent", parent)
                ress.append(result)
        return ress

    def checked_elements(self, element, obj=None):
        if element.Nodes.Count > 0:
            for node in element.Nodes:
                res = {}
                res.setdefault("active", node.Checked)
                res.setdefault("name", node.Text)
                res.setdefault("childs", [])
                if node.Nodes.Count > 0:
                    self.checked_elements(node, obj=res["childs"])
                obj.append(res)


    def active_button(self, sender, e):
        res = []
        self.checked_elements(self.tree, obj=res)
        config_path = os.path.join(os.environ["PROGRAMDATA"], r"Autodesk\Revit\Addins\2019\RedBim\config.json")
        with open(config_path, "w") as f:
            json.dump(res, f)
            f.close()
        message("Плагины появятся при перезапуске Revit")
        self.Close()




    def find_all_pushbuttons(self):
        tabs = self.find_element(SCRIPTS_PATH, ".tab")
        for i in tabs:
            i.setdefault("node", TreeNode())
            i["node"].Text = i["name"]
            self.tree.Nodes.Add(i["node"])
            panels = self.find_element(i["path"], ".panel", parent=i)
            for panel in panels:
                panel.setdefault("node", TreeNode())
                panel["node"].Text = panel["name"]
                i["node"].Nodes.Add(panel["node"])
                pbs = self.find_element(panel["path"], ".pushbutton", parent=panel)
                for pb in pbs:
                    pb.setdefault("node", TreeNode())
                    pb["node"].Text = pb["name"]
                    panel["node"].Nodes.Add(pb["node"])

    # def create_tab_checkbox()

# form = RedBimSetting()
# form.Show()

def get_all_tabs(sender=None, e=None):
    config_path = os.path.join(os.environ["PROGRAMDATA"], r"Autodesk\Revit\Addins\2019\RedBim\config.json")
    with open(config_path, "r") as f:
        data = json.load(f)
        f.close()
    all_tab = []
    script_path = DIR_SCRIPTS
    # echo("Получаем имена всех вкладок с  " + script_path)
    files = os.listdir(script_path)
    # echo(files)
    # echo("____________________", "Создаем все вкладки")
    # echo('\n')
    # test = False
    for file in files:
        # if not test:
        #     message(os.path.join(script_path, file))
        #     test = True
        os.path.isdir(os.path.join(script_path, file))
        is_tab = re.search(r".tab$", file)
        if is_tab:
            # if section == "all" or section in file or ("test" in file and developer):
            for i in data:
                if i["name"] == file:
                    if i["active"]:
                        all_tab.append(RB_Tab(file, script_path, childs=i["childs"]))
                    break
            else:
                all_tab.append(RB_Tab(file, script_path))
        # echo('\n')
    if not all_tab:
        echo("Папок со скриптами нет")
    return all_tab

def find_all_tab(developer=False, section="all"):
    config_path = os.path.join(os.environ["PROGRAMDATA"], r"Autodesk\Revit\Addins\2019\RedBim\config.json")
    if not os.path.exists(config_path):
        form = RedBimSetting()
        form.Show()
    else:
        get_all_tabs()
    """Находит все вкладки в script_path."""
    # all_tab = []
    # script_path = DIR_SCRIPTS
    # # echo("Получаем имена всех вкладок с  " + script_path)
    # files = os.listdir(script_path)
    # # echo(files)
    # # echo("____________________", "Создаем все вкладки")
    # # echo('\n')
    # for file in files:
    #     os.path.isdir(os.path.join(script_path, file))
    #     is_tab = re.search(r".tab$", file)
    #     if is_tab:
    #         if section == "all" or section in file or ("test" in file and developer):
    #             all_tab.append(RB_Tab(file, script_path))
    #     # echo('\n')
    # if not all_tab:
    #     echo("Папок со скриптами нет")
    # return all_tab


__all__ = ['find_all_tab']
