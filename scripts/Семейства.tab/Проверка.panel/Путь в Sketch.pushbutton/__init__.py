import os

path = r"L:\09_Программы\WeandrevitGates\WeandrevitGates_2019\Weandrevit\RebarSketch\library"

def get_files(path, familyes):
    if os.path.isdir(path):
        all_dirs = os.listdir(path)
        for i in all_dirs:
            curpath = os.path.join(path, i)
            fam_file = os.path.join(curpath, "families"+".txt")
            # echo(fam_file)
            if os.path.exists(fam_file):
                with open(fam_file, 'rb') as f:
                    for i in list(f):
                        try:
                            i = i.replace("ï»¿", "")
                            i = i.decode("utf-8")
                            i = i.replace("\ufeff", "").strip()
                            # echo(curpath.replace(path, ""))
                            familyes.setdefault(i, [])
                            familyes[i].append(curpath)
                        except:
                            echo("Ошибка с чтением файла", fam_file)
            if os.path.isdir(curpath):
                # echo(curpath)
                get_files(curpath, familyes)

doc = __revit__.ActiveUIDocument.Document
selection = [doc.GetElement(elId) for elId in __revit__.ActiveUIDocument.Selection.GetElementIds()]
el = selection[0]
if el.Category.Name == "Несущая арматура":
    par = el.LookupParameter("Форма")
    if par:
        shape = doc.GetElement(par.AsElementId())
        par = shape.LookupParameter("Имя типа").AsString()
    else:
        if hasattr(el, "Symbol"):
            el = el.Symbol
            if hasattr(el, "Family"):
                el = el.Family
                par = el.Name

    res = None
    if not par:
        message("Ошибка получения параметра")
    else:
        familyes = {}
        get_files(path, familyes)
        if par in familyes.keys():
            res = familyes[par]
            if res:
                message("\n\r".join(res))
        else:
            message("Картинки нет в базе")
else:

    message("Выбрана не арматрура")

