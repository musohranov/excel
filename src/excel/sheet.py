# coding: utf8

"""
Лист.
"""

from .cell import cell
from .cell.expression_value import ExpressionValue
from .cell.ref_value import RefValue

__all__ = ['Sheet', 'SheetSize']


class Sheet:
    """
    Лист.
    """

    def __init__(self, line):
        """
        Конструктор.

        :param str line: Строка задающая размер листа.
        :raises ValueError:
        """

        self._size = SheetSize.parser(line)
        self._cell_list = {}

    def get_size(self):
        """
        Получить размер листа.
        :rtype: SheetSize
        """

        return self._size

    def add_line(self, line):
        """
        Добавить строку.

        :param str line: Строка со значениями в ячейках.
        :raises ValueError:
        """

        error_text = f'Строка со значением ячеек должна содержать ' \
                     f'"{self._size.x}" выражений разделенных символом табуляции!'

        if not isinstance(line, str):
            raise ValueError(error_text)

        cell_value_list = line.split('\t')
        if not (len(cell_value_list) == self._size.x):
            raise ValueError(error_text)

        if len(self._cell_list) >= self._size.y * self._size.x:
            raise ValueError('Достигнут предел размерности таблицы по вертикали!')

        # Заполнить текущую строку ячейками
        line_number = int(len(self._cell_list) / self._size.x) + 1
        for i, value in enumerate(cell_value_list):
            self._cell_list[(i + 1, line_number)] = cell.parser(value)

    def calculate(self):
        """
        Рассчитать значения.

        :rtype: dict
        :return Ключом является кортеж (x, y), значением вычисленное выражение.
        """

        if not (len(self._cell_list) == (self._size.x * self._size.y)):
            raise RuntimeError(f'Инициализация не закончена. '
                               f'Кол-во заданных ячеек "{len(self._cell_list)}" из "{self._size.x * self._size.y}"')

        sheet_cell_value = {}

        # Вычислить результат для всех не выражений.
        for key, cell_value in self._cell_list.items():
            sheet_cell_value[key] = \
                cell_value.get_value() if not isinstance(cell_value, ExpressionValue) else cell_value

        # Вычислить результат для всех выражений.
        for key, cell_value in sheet_cell_value.items():
            if isinstance(cell_value, ExpressionValue):
                ExpressionValue._calc_expression(key, cell_value.get_value(), sheet_cell_value)

        return sheet_cell_value


class SheetSize:
    """
    Размер листа.

    Максимальные размеры листа расчитываются исходя из утверждения
    'Ссылки на ячейки состоят из одной латинской буквы и следующей за ней цифры'.
    """

    # Максимальный размер листа по вертикали (1-9)
    Max_Y = 9

    # Максимальный размер листа по горизонтали (A-Z)
    Max_X = 26

    def __init__(self, y, x):
        """
        Конструктор.

        :param int y: Размер по вертикали.
        :param int x: Размер по горизонтали.

        :raises ValueError:
        """

        if not(isinstance(y, int) and 0 < y <= self.Max_Y):
            raise ValueError(f'Размер по вертикали должен лежать в диапазоне 1-{self.Max_Y}!')
        self._y = y

        if not(isinstance(x, int) and 0 < x <= self.Max_X):
            raise ValueError(f'Размер по горизонтали должен лежать в диапазоне 1-{self.Max_X}!')
        self._x = x

    @property
    def y(self):
        """
        Получить размер по вертикали.
        :rtype: int
        """
        return self._y

    @property
    def x(self):
        """
        Получить размер по горизонтали.
        :rtype: int
        """
        return self._x

    @classmethod
    def parser(cls, line):
        """
        Разобрать размер листа.

        :param str line: Строка (в формате Y\tX).
        :rtype: SheetSize

        :raises ValueError:
        """

        error_text = f'Строка с размером листа должна быть в формате "<1-{cls.Max_Y}>/t<1-{cls.Max_X}>"!'

        if not (isinstance(line, str) and line):
            raise ValueError(error_text)

        values = line.split('\t')
        if not (len(values) == 2 and values[0].isdigit() and values[1].isdigit()):
            raise ValueError(error_text)

        return SheetSize(int(values[0]), int(values[1]))
