"""
Механим определения значения ячейки
"""

from abc import ABC
from typing import Any


class CellValue(ABC):
    """
    Значение ячейки
    """

    def __init__(self):
        """
        """

        self._value: Any = None

    def get_value(self) -> Any:
        """
        Получить занчение
        """

        return self._value

    @staticmethod
    def parser(value: str) -> 'CellValue':
        """
        Разобрать значение ячейки.

        :param value: Строковое значение ячейки
        :raise: ValueError
        """

        from excel.cell.empty_value import EmptyValue
        from excel.cell.number_value import NumberValue
        from excel.cell.text_value import TextValue
        from excel.cell.expression_value import ExpressionValue

        for value_class in [EmptyValue, NumberValue, TextValue, ExpressionValue]:
            try:
                return value_class(value)
            except ValueError:
                pass

        raise ValueError(f'Значение "{value}" не соответствует ни одному типу!')
