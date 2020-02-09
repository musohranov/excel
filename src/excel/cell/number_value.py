"""
Тип ячейки 'Числовое значение'
"""

from excel.cell.cell import CellValue


class NumberValue(CellValue):
    """
    Число.
    Целое положительное.
    """

    def __init__(self, value: str):
        """
        :param str value: Строка задающая значение
        :raise: ValueError
        """

        super().__init__()

        if not (isinstance(value, str) and value.isdigit() and int(value) >= 0):
            raise ValueError(f'Значение "{value}" не является целым положительным числом!')

        self._value = int(value)
