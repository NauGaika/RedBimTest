# -*- coding: utf-8 -*-
from common_scripts import echo
import json


class Instalation_plan_tests(object):
    def __init__(self):
        super(Instalation_plan_tests, self).__init__()
        self.test_get_dict_from_file()
        self.test_position_comparation()

    def test_get_dict_from_file(self):
        test_obj = {
            "BuildingAssembly": [
                {
                    "precast": [
                        {
                            "mark": "3НСКгб 453.306.36-71",
                            "position": {
                                "Y": -340.0,
                                "X": -340.0,
                                "Z": 0.0
                            },
                            "rotation": 0.0,
                            "colorIndex": "0199_к11_1-1-1"
                        },
                        {
                            "mark": "3НСКгб 599.306.36-87",
                            "position": {
                                "Y": 5992.0,
                                "X": -340.0,
                                "Z": 0.0
                            },
                            "rotation": 1.5707953071795995,
                            "colorIndex": "0199_к11_2-2-0"
                        }],
                    "section": "1",
                    "level": "2"
                }]
        }

        result = {
            "1": {
                "2": [
                    {
                        "mark":  "3НСКгб 453.306.36-71",
                        "position": {"X": -340.0, "Y": -340.0, "Z": 0.0},
                        "rotation": 0.0,
                        "colorIndex": "0199_к11_1-1-1"
                    },
                    {
                        "mark":  "3НСКгб 599.306.36-87",
                        "position": {"X": -340.0, "Y": 5992.0, "Z": 0.0},
                        "rotation": 1.57080,
                        "colorIndex": "0199_к11_2-2-0"
                    }
                ]
            }
        }

        assert self.get_all_panels_from_dict(
            test_obj) == result, "Не верное преобразование"

    def test_position_comparation(self):
        p1 = {
            "mark": "ЗНСКг-[100.СБП]-599.324.36-3.2",
            "position": {
                "Y": 21340,
                "X": 27892.5,
                "Z": 0
            },
            "rotation": 3.14159,
            "colorIndex": None
        }
        p2 = {
            "mark": "ЗНСКг-[100.СБП]-599.324.36-3.1",
            "position": {
                "Y": 21370,
                "X": 27882.5,
                "Z": 0
            },
            "rotation": 3.14159,
            "colorIndex": None
        }
        p3 = {
            "mark": "ЗНСКг-[100.СБП]-599.324.36-3.1",
            "position": {
                "Y": 21340,
                "X": 27892.5,
                "Z": 0
            },
            "rotation": 3.14159,
            "colorIndex": None
        }
        p4 = {
            "mark": "ЗНСКг-[100.СБП]-599.324.36-3.1",
            "position": {
                "Y": 21570,
                "X": 27882.5,
                "Z": 0
            },
            "rotation": 3.14159,
            "colorIndex": None
        }

        assert self.compare_position(
            p1, p2) == True, "Не выполняется равенство панелей"
        assert self.compare_position(
            p3, p4) is None, "Не выполняется не равенство панелей"
