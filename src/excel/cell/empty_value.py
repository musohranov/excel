"""
Тип ячейки 'Пустое значение'
"""

from excel.cell.cell import CellValue


class EmptyValue(CellValue):
    """
    Пустое значение
    """

    def __init__(self, value: str):
        """
        :param value: Строка задающая значение
        :raise: ValueError
        """

        super().__init__()

        if not (isinstance(value, str) and value == ''):
            raise ValueError(f'Значение "{value}" не является пустым!')

        self._value: str = value
