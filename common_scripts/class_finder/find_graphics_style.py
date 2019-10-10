# coding: utf8
from Autodesk.Revit.DB import FilteredElementCollector, GraphicsStyle
from common_scripts import echo


def find_graphics_style(*names):
    """Ищет графический стиль линии по имени или части имени."""
    doc = __revit__.ActiveUIDocument.Document
    els = FilteredElementCollector(doc).OfClass(GraphicsStyle).ToElements()
    els = list(els)
    default_style = els[0]
    for name in names:
        els = finder_iterator_by_name(els, name)
    if els:
        return els[0]
    return default_style

def finder_iterator_by_name(arr, name):
    if not isinstance(arr, list):
        arr = list(arr)
    new_arr = []
    name = name.lower()
    for el in arr:
        if name in el.Name.lower():
            echo(name, el.Name.lower())
            new_arr.append(el)
    return new_arr
