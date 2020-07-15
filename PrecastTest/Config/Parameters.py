# -*- coding: utf-8 -*-
from Autodesk.Revit.DB import BuiltInCategory, BuiltInParameterGroup


panel_category = [BuiltInCategory.OST_Walls, BuiltInCategory.OST_Columns] # Категории панелей
window_category = [BuiltInCategory.OST_Windows, BuiltInCategory.OST_GenericModel] # Категории окон
connection_category = [BuiltInCategory.OST_StructConnections] # Категории закладных
material_category = [BuiltInCategory.OST_Materials] # Категории материалов


project_prefixes = {
    "geometrical_panel": ""
}

project_parameters = {
    "BDS_ElementType": {
        "description": "Тип элемента",
        "type": "Currency",
        "is_type": False,
        "change_in_group": True,
        "in_family": True,
        "categoryes": panel_category + window_category + connection_category,
        "group": BuiltInParameterGroup.PG_IDENTITY_DATA
    },
    "BDS_Mass": {
        "description": "Масса в кг",
        "type": "Currency",
        "is_type": False,
        "change_in_group": True,
        "in_family": False,
        "categoryes": panel_category + connection_category,
        "group": BuiltInParameterGroup.PG_DATA
    },
    "BDS_Volume": {
        "description": "Объем в м3",
        "type": "Currency",
        "is_type": False,
        "change_in_group": True,
        "in_family": False,
        "categoryes": panel_category + connection_category,
        "group": BuiltInParameterGroup.PG_DATA
    },
    "BDS_Series": {
        "description": "Серия элемента например сэм2к",
        "type": "Text",
        "is_type": True,
        "change_in_group": True,
        "in_family": True,
        "categoryes": panel_category,
        "group": BuiltInParameterGroup.PG_IDENTITY_DATA
    },
    "BDS_FacadeType": {
        "description": "Тип фасада Кг - кирпич",
        "type": "Text",
        "is_type": True,
        "change_in_group": True,
        "in_family": True,
        "categoryes": panel_category,
        "group": BuiltInParameterGroup.PG_IDENTITY_DATA
    },
    "BDS_MarkPrefix": {
        "description": "Префикс марки. например 3НС",
        "type": "Text",
        "is_type": True,
        "change_in_group": False,
        "in_family": True,
        "categoryes": panel_category,
        "group": BuiltInParameterGroup.PG_IDENTITY_DATA
    },
    "BDS_MarkSubPrefix": {
        "description": "Сабпрефикс. Например СН",
        "type": "Text",
        "is_type": True,
        "change_in_group": False,
        "in_family": True,
        "categoryes": panel_category,
        "group": BuiltInParameterGroup.PG_IDENTITY_DATA
    },
    "BDS_ConstructionType": {
        "description": "Тип конструкции outwall ...",
        "type": "Text",
        "is_type": True,
        "change_in_group": False,
        "in_family": True,
        "categoryes": panel_category,
        "group": BuiltInParameterGroup.PG_IDENTITY_DATA
    },
    "BDS_AdvanceTag": {
        "description": """
        Предвартиельная марка. назначается если на сервере
        Назначается если панели нет в базе.
        """,
        "type": "Text",
        "is_type": False,
        "change_in_group": True,
        "in_family": False,
        "categoryes": panel_category,
        "group": BuiltInParameterGroup.PG_IDENTITY_DATA
    },
    "BDS_Tag": {
        "description": """
        Марка, которая выносится на чертеж для панелей
        Для закладных - марка выносящаяся в спецификацию.
        Для связей - марка связи
        Для составных связи - марка составной
        """,
        "type": "Text",
        "is_type": False,
        "change_in_group": True,
        "in_family": False,
        "categoryes": panel_category + window_category + connection_category,
        "group": BuiltInParameterGroup.PG_IDENTITY_DATA
    },
    "BDS_SystemTag": {
        "description": """
        Марка которая вернулась с сервера
        """,
        "type": "Text",
        "is_type": False,
        "change_in_group": True,
        "in_family": False,
        "categoryes": panel_category + connection_category + window_category,
        "group": BuiltInParameterGroup.PG_IDENTITY_DATA
    },
    "BDS_Hole": {
        "description": """
        Поле для записи окон принадлежащих панели.
        Записываются размеры и количество.
        В формате 1400х1200(2шт), 1600х1800
        """,
        "type": "Text",
        "is_type": False,
        "change_in_group": True,
        "in_family": False,
        "categoryes": panel_category,
        "group": BuiltInParameterGroup.PG_DATA
    },
    "BDS_Length": {
        "description": """
        Длина окна, панели итд для выгрузки
        """,
        "type": "Currency",
        "is_type": False,
        "change_in_group": True,
        "in_family": True,
        "categoryes": panel_category + window_category,
        "group": BuiltInParameterGroup.PG_DATA
    },
    "BDS_LayerNumber": {
        "description": """
        Ширина
        """,
        "type": "Integer",
        "is_type": False,
        "change_in_group": False,
        "in_family": False,
        "categoryes": material_category,
        "group": BuiltInParameterGroup.PG_DATA
    },
    "BDS_Density": {
        "description": """
        Ширина
        """,
        "type": "Currency",
        "is_type": False,
        "change_in_group": False,
        "in_family": False,
        "categoryes": material_category,
        "group": BuiltInParameterGroup.PG_DATA
    },
    "JSON": {
        "description": """
        Системный параметр в котором описывается JSON
        Передаваемый на сервер.
        """,
        "type": "Currency",
        "is_type": False,
        "change_in_group": True,
        "in_family": False,
        "categoryes": panel_category + window_category + connection_category,
        "group": BuiltInParameterGroup.PG_DATA
    },
    "BDS_ColoristicsTag_Floor01": {
        "description": """
        Коллористическая марка.
        """,
        "type": "Text",
        "is_type": False,
        "change_in_group": True,
        "in_family": False,
        "categoryes": panel_category,
        "group": BuiltInParameterGroup.PG_DATA
    },
    "BDS_ColoristicsTag_Floor02": {
        "description": """
        Коллористическая марка.
        """,
        "type": "Text",
        "is_type": False,
        "change_in_group": True,
        "in_family": False,
        "categoryes": panel_category,
        "group": BuiltInParameterGroup.PG_DATA
    },
    "BDS_ColoristicsTag_Floor03": {
        "description": """
        Коллористическая марка.
        """,
        "type": "Text",
        "is_type": False,
        "change_in_group": True,
        "in_family": False,
        "categoryes": panel_category,
        "group": BuiltInParameterGroup.PG_DATA
    },
    "BDS_ColoristicsTag_Floor04": {
        "description": """
        Коллористическая марка.
        """,
        "type": "Text",
        "is_type": False,
        "change_in_group": True,
        "in_family": False,
        "categoryes": panel_category,
        "group": BuiltInParameterGroup.PG_DATA
    },
    "BDS_ColoristicsTag_Floor05": {
        "description": """
        Коллористическая марка.
        """,
        "type": "Text",
        "is_type": False,
        "change_in_group": True,
        "in_family": False,
        "categoryes": panel_category,
        "group": BuiltInParameterGroup.PG_DATA
    },
    "BDS_ColoristicsTag_Floor06": {
        "description": """
        Коллористическая марка.
        """,
        "type": "Text",
        "is_type": False,
        "change_in_group": True,
        "in_family": False,
        "categoryes": panel_category,
        "group": BuiltInParameterGroup.PG_DATA
    },
    "BDS_ColoristicsTag_Floor07": {
        "description": """
        Коллористическая марка.
        """,
        "type": "Text",
        "is_type": False,
        "change_in_group": True,
        "in_family": False,
        "categoryes": panel_category,
        "group": BuiltInParameterGroup.PG_DATA
    },
    "BDS_ColoristicsTag_Floor08": {
        "description": """
        Коллористическая марка.
        """,
        "type": "Text",
        "is_type": False,
        "change_in_group": True,
        "in_family": False,
        "categoryes": panel_category,
        "group": BuiltInParameterGroup.PG_DATA
    },
    "BDS_ColoristicsTag_Floor09": {
        "description": """
        Коллористическая марка.
        """,
        "type": "Text",
        "is_type": False,
        "change_in_group": True,
        "in_family": False,
        "categoryes": panel_category,
        "group": BuiltInParameterGroup.PG_DATA
    },
    "BDS_ColoristicsTag_Floor10": {
        "description": """
        Коллористическая марка.
        """,
        "type": "Text",
        "is_type": False,
        "change_in_group": True,
        "in_family": False,
        "categoryes": panel_category,
        "group": BuiltInParameterGroup.PG_DATA
    },
    "BDS_ColoristicsTag_Floor11": {
        "description": """
        Коллористическая марка.
        """,
        "type": "Text",
        "is_type": False,
        "change_in_group": True,
        "in_family": False,
        "categoryes": panel_category,
        "group": BuiltInParameterGroup.PG_DATA
    },
    "BDS_ColoristicsTag_Floor01": {
        "description": """
        Коллористическая марка.
        """,
        "type": "Text",
        "is_type": False,
        "change_in_group": True,
        "in_family": False,
        "categoryes": panel_category,
        "group": BuiltInParameterGroup.PG_DATA
    },
    "BDS_ColoristicsTag_Floor12": {
        "description": """
        Коллористическая марка.
        """,
        "type": "Text",
        "is_type": False,
        "change_in_group": True,
        "in_family": False,
        "categoryes": panel_category,
        "group": BuiltInParameterGroup.PG_DATA
    },
    "BDS_ColoristicsTag_Floor13": {
        "description": """
        Коллористическая марка.
        """,
        "type": "Text",
        "is_type": False,
        "change_in_group": True,
        "in_family": False,
        "categoryes": panel_category,
        "group": BuiltInParameterGroup.PG_DATA
    },
    "BDS_ColoristicsTag_Floor14": {
        "description": """
        Коллористическая марка.
        """,
        "type": "Text",
        "is_type": False,
        "change_in_group": True,
        "in_family": False,
        "categoryes": panel_category,
        "group": BuiltInParameterGroup.PG_DATA
    },
    "BDS_ColoristicsTag_Floor15": {
        "description": """
        Коллористическая марка.
        """,
        "type": "Text",
        "is_type": False,
        "change_in_group": True,
        "in_family": False,
        "categoryes": panel_category,
        "group": BuiltInParameterGroup.PG_DATA
    },
    "BDS_ColoristicsTag_Floor16": {
        "description": """
        Коллористическая марка.
        """,
        "type": "Text",
        "is_type": False,
        "change_in_group": True,
        "in_family": False,
        "categoryes": panel_category,
        "group": BuiltInParameterGroup.PG_DATA
    },
    "BDS_ColoristicsTag_Floor17": {
        "description": """
        Коллористическая марка.
        """,
        "type": "Text",
        "is_type": False,
        "change_in_group": True,
        "in_family": False,
        "categoryes": panel_category,
        "group": BuiltInParameterGroup.PG_DATA
    },
    "BDS_ColoristicsTag_Floor18": {
        "description": """
        Коллористическая марка.
        """,
        "type": "Text",
        "is_type": False,
        "change_in_group": True,
        "in_family": False,
        "categoryes": panel_category,
        "group": BuiltInParameterGroup.PG_DATA
    },
    "BDS_ColoristicsTag_Floor19": {
        "description": """
        Коллористическая марка.
        """,
        "type": "Text",
        "is_type": False,
        "change_in_group": True,
        "in_family": False,
        "categoryes": panel_category,
        "group": BuiltInParameterGroup.PG_DATA
    },
    "BDS_ColoristicsTag_Floor20": {
        "description": """
        Коллористическая марка.
        """,
        "type": "Text",
        "is_type": False,
        "change_in_group": True,
        "in_family": False,
        "categoryes": panel_category,
        "group": BuiltInParameterGroup.PG_DATA
    },
    "BDS_ColoristicsTag_Floor21": {
        "description": """
        Коллористическая марка.
        """,
        "type": "Text",
        "is_type": False,
        "change_in_group": True,
        "in_family": False,
        "categoryes": panel_category,
        "group": BuiltInParameterGroup.PG_DATA
    },
    "BDS_ColoristicsTag_Floor22": {
        "description": """
        Коллористическая марка.
        """,
        "type": "Text",
        "is_type": False,
        "change_in_group": True,
        "in_family": False,
        "categoryes": panel_category,
        "group": BuiltInParameterGroup.PG_DATA
    },
    "BDS_ColoristicsTag_Floor23": {
        "description": """
        Коллористическая марка.
        """,
        "type": "Text",
        "is_type": False,
        "change_in_group": True,
        "in_family": False,
        "categoryes": panel_category,
        "group": BuiltInParameterGroup.PG_DATA
    },
    "BDS_ColoristicsTag_Floor24": {
        "description": """
        Коллористическая марка.
        """,
        "type": "Text",
        "is_type": False,
        "change_in_group": True,
        "in_family": False,
        "categoryes": panel_category,
        "group": BuiltInParameterGroup.PG_DATA
    },
    "BDS_ColoristicsTag_Floor25": {
        "description": """
        Коллористическая марка.
        """,
        "type": "Text",
        "is_type": False,
        "change_in_group": True,
        "in_family": False,
        "categoryes": panel_category,
        "group": BuiltInParameterGroup.PG_DATA
    },
    "IFC_Export": {
        "description": """
        Доп параметры для экспорта
        """,
        "type": "Text",
        "is_type": False,
        "change_in_group": True,
        "in_family": False,
        "categoryes": panel_category + window_category + connection_category,
        "group": BuiltInParameterGroup.PG_DATA
    },
    "BDS_Modifying": {
        "description": """
        Здесь указываются все модификаторы панели.
        Консоли, окна, торцы итд
        Запись производится в строчку.
        Разделитель пар |

        Разделитель ключа и значения :
        """,
        "type": "Text",
        "is_type": False,
        "change_in_group": True,
        "in_family": False,
        "categoryes": panel_category + window_category,
        "group": BuiltInParameterGroup.PG_DATA
    },
    "BDS_Window": {
        "description": """
        Наличие в панели окна.
        Заполняется с помощью плагина.
        """,
        "type": "Bool",
        "is_type": False,
        "change_in_group": True,
        "in_family": False,
        "categoryes": panel_category + window_category,
        "group": BuiltInParameterGroup.PG_DATA
    },
    "BDS_Balcony": {
        "description": """
        Наличие в панели окна.
        Заполняется с помощью плагина.
        """,
        "type": "Bool",
        "is_type": False,
        "change_in_group": True,
        "in_family": False,
        "categoryes": panel_category + window_category,
        "group": BuiltInParameterGroup.PG_DATA
    },
    "BDS_Door": {
        "description": """
        Наличие в панели окна.
        Заполняется с помощью плагина.
        """,
        "type": "Bool",
        "is_type": False,
        "change_in_group": True,
        "in_family": False,
        "categoryes": panel_category + window_category,
        "group": BuiltInParameterGroup.PG_DATA
    },
    "BDS_PositionType": {
        "description": """
        Наличие в панели окна.
        Заполняется с помощью плагина.
        """,
        "type": "Bool",
        "is_type": False,
        "change_in_group": True,
        "in_family": False,
        "categoryes": window_category,
        "group": BuiltInParameterGroup.PG_DATA
    }
}
