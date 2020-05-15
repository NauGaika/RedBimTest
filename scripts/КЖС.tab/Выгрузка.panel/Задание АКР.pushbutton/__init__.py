from Precast import Precast
from Autodesk.Revit.DB import Transaction
from System.Windows.Forms import FolderBrowserDialog, DialogResult

doc = __revit__.ActiveUIDocument.Document

dir_path = FolderBrowserDialog()
res = dir_path.ShowDialog()
if res == DialogResult.OK and dir_path.SelectedPath:
    dir_path = dir_path.SelectedPath
    with Transaction(doc, "Объединение панелей с элементами узла") as t:
        t.Start()
        obj = Precast(__revit__, create_new_panel=True, old_format_path=dir_path)
        obj.define_section()
        t.Commit()