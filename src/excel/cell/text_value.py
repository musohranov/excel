"""
Тип ячейки 'Текст'
"""

from excel.cell.cell import CellValue


class TextValue(CellValue):
    """
    Текст.
    Начинается с символа '
    """

    def __init__(self, value: str):
        """
        :param str value: Строка задающая значение
        :raise: ValueError
        """

        super().__init__()

        if not (isinstance(value, str) and len(value) > 0 and value[0] == "'"):
            raise ValueError(f'Значение "{value}" не является текстом!')

        self._value: str = value[1:]
