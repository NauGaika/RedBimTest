# -*- coding: utf-8 -*-
from common_scripts import echo
from common_scripts.line_print import Line_printer


class Instalation_plan_json(object):
    def grids_to_dict(self, grids, elevation=True):
        grid_objects = []
        for i in grids.values():
            grid_objects.append(self.grid_to_dict(i))
        grid_objects.sort(key=lambda x: x["local"])
        if elevation:
            grid_objects = {
                "Ismm": True,
                "Grids": grid_objects,
                "Levels": self.levels
            }
        return grid_objects

    def grid_to_dict(self, grid):
        "Преобразовывает ось в необходимую для выгрузки"
        # Line_printer.print_arc(grid["origin"], color="иня")
        grid["direction"] = grid["direction"].Negate() if (round(
            grid["direction"].X, 5) < 0 or round(grid["direction"].Y, 5) < 0) else grid["direction"]
        return {
            "local": grid["name"],
            "position": self.make_xyz(grid["origin"], round_count=1),
            "rotation": self.make_xyz(grid["direction"], to_mm=False),
            "global": grid["global"]
        }

    @staticmethod
    def make_xyz(point, to_mm=True, round_count=5, nullable_z=False, nullable_x=False, nullable_y=False):
        "Преобразовывает ревитовские оси в json."
        return {
            "X": (1 - nullable_x) * round(point.X * (304.8 * to_mm + (1 - to_mm)), round_count),
            "Y": (1 - nullable_y) * round(point.Y * (304.8 * to_mm + (1 - to_mm)), round_count),
            "Z": (1 - nullable_z) * round(point.Z * (304.8 * to_mm + (1 - to_mm)), round_count)
        }

    def get_all_panels_from_dict(self, obj):
        "Получаем панели из того, что возвращает колористика."
        res_obj = {}
        for level_obj in obj["BuildingAssembly"]:
            section = level_obj["section"]
            level = level_obj["level"]
            res_obj.setdefault(section, {})
            res_obj[section].setdefault(level, [])
            for panel in level_obj["precast"]:
                # echo(panel.keys())
                res_obj[section][level].append({
                    "mark":  panel["mark"],
                    "position": panel["position"],
                    "rotation": round(panel["rotation"], 5),
                    "colorIndex": panel["colorIndex"]
                })
        return res_obj
