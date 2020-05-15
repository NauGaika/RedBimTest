panel_category = ["OST_Walls", "OST_Columns"]
window_category = ["OST_Windows", "OST_GenericModel"]
material_category = ["OST_Matrials"]


project_prefixes = {
    "geometrical_panel": ""
}

project_parameters = [
    {
        "name": "BDS_ElementType",
        "description": "Тип элемента",
        "type": "Currency",
        "is_type": False,
        "change_in_group": True,
        "in_family": True,
        "categoryes": panel_category,
        "group": None
    },
    {
        "name": "BDS_Mass",
        "description": "Масса в кг",
        "type": "Currency",
        "is_type": False,
        "change_in_group": True,
        "in_family": True,
        "categoryes": panel_category,
        "group": None
    },
    {
        "name": "BDS_Volume",
        "description": "Объем в м3",
        "type": "Currency",
        "is_type": False,
        "change_in_group": True,
        "in_family": True,
        "categoryes": panel_category,
        "group": None
    },
    {
        "name": "BDS_Series",
        "description": "Серия элемента например сэм2к",
        "type": "Text",
        "is_type": True,
        "change_in_group": True,
        "in_family": True,
        "categoryes": panel_category,
        "group": None
    },
    {
        "name": "BDS_FacadeType",
        "description": "Тип фасада Кг - кирпич",
        "type": "Text",
        "is_type": True,
        "change_in_group": True,
        "in_family": True,
        "categoryes": panel_category,
        "group": None
    },
    {
        "name": "BDS_MarkPrefix",
        "description": "Префикс марки. например 3НС",
        "type": "Text",
        "is_type": True,
        "change_in_group": False,
        "in_family": True,
        "categoryes": panel_category,
        "group": None
    },
    {
        "name": "BDS_MarkSubPrefix",
        "description": "Сабпрефикс. Например СН",
        "type": "Text",
        "is_type": True,
        "change_in_group": False,
        "in_family": True,
        "categoryes": panel_category,
        "group": None
    },
    {
        "name": "BDS_ConstructionType",
        "description": "Тип конструкции outwall ...",
        "type": "Text",
        "is_type": True,
        "change_in_group": False,
        "in_family": True,
        "categoryes": panel_category,
        "group": None
    },
    {
        "name": "BDS_AdvanceTag",
        "description": """
        Предвартиельная марка. назначается если на сервере
        Назначается если панели нет в базе.
        """,
        "type": "Text",
        "is_type": False,
        "change_in_group": True,
        "in_family": False,
        "categoryes": panel_category,
        "group": None
    },
    {
        "name": "BDS_SystemTag",
        "description": """
        Марка которая вернулась с сервера
        """,
        "type": "Text",
        "is_type": False,
        "change_in_group": True,
        "in_family": False,
        "categoryes": panel_category,
        "group": None
    },
    {
        "name": "BDS_Hole",
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
        "group": None
    },
    {
        "name": "BDS_Length",
        "description": """
        Длина окна, панели итд для выгрузки
        """,
        "type": "Currency",
        "is_type": False,
        "change_in_group": True,
        "in_family": True,
        "categoryes": panel_category + window_category,
        "group": None
    },
    {
        "name": "BDS_LayerNumber",
        "description": """
        Ширина
        """,
        "type": "Integer",
        "is_type": False,
        "change_in_group": False,
        "in_family": False,
        "categoryes": material_category,
        "group": None
    },
    {
        "name": "BDS_Density",
        "description": """
        Ширина
        """,
        "type": "Currency",
        "is_type": False,
        "change_in_group": False,
        "in_family": False,
        "categoryes": material_category,
        "group": None
    }
]
