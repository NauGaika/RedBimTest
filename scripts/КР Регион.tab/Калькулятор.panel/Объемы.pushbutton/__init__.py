doc = __revit__.ActiveUIDocument.Document
selection = [doc.GetElement(elId) for elId in __revit__.ActiveUIDocument.Selection.GetElementIds()]

value = 0
plosc = 0
length = 0
for i in selection:
    if i.GetParameters('Объем'):
        value += i.GetParameters('Объем')[0].AsDouble()
    if i.GetParameters('Площадь'):
        plosc += i.GetParameters('Площадь')[0].AsDouble()
    if i.GetParameters('Длина'):
        length += i.GetParameters('Длина')[0].AsDouble()

message_str = """
Длина = {}м
Площадь = {}м2 
Объем = {}м3 
""".format(
    round(length * 0.3048 *10)/10,
    round(plosc * 0.3048 * 0.3048*10)/10,
    round(value * 10 * 0.3048 * 0.3048 * 0.3048) / 10
    )

message(message_str)