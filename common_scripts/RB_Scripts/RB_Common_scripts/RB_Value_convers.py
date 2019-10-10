# coding: utf8
"""Модуль по преобразованию велечин."""


def to_feet(mm):
    """Из мм в футы."""
    return mm*0.00328084


def to_mm(mm):
    """Из футов в мм."""
    return round(mm/0.00328084)


__all__ = ['to_feet', 'to_mm']
