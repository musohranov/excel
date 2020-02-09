"""
Механика листа.
Предоставляется функциональность добавления расчетных строк с ячейками, с последующей механикой расчета.
"""

from excel.cell.cell import CellValue
from excel.cell.expression_value import ExpressionValue


class Sheet:
    """
    Лист
    """

    def __init__(self, size_line: str):
        """
        :param size_line: Строка задающая размер листа
        :raise: ValueError
        """

        self._size: SheetSize = SheetSize.parser(size_line)
        self._cell_list: dict = {}

    def get_size(self) -> 'SheetSize':
        """
        Получить размер листа
        """

        return self._size

    def add_line(self, line: str):
        """
        Добавить строку с ячейками

        :param line: Строка со значениями в ячейках
        :raise: ValueError
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
            self._cell_list[(i + 1, line_number)] = CellValue.parser(value)

    def calculate(self) -> dict:
        """
        Рассчитать значения
        :return Ключом является кортеж (x, y), значением вычисленное выражение
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
                cell_value.calc(key, sheet_cell_value)

        return sheet_cell_value


class SheetSize:
    """
    Размер листа.

    Максимальные размеры листа расчитываются исходя из утверждения
    'Ссылки на ячейки состоят из одной латинской буквы и следующей за ней цифры'.
    """

    MAX_Y = 9
    """
    Максимальный размер листа по вертикали (1-9)
    """

    MAX_X = 26
    """
    Максимальный размер листа по горизонтали (A-Z)
    """

    def __init__(self, y: int, x: int):
        """
        :param y: Размер по вертикали
        :param x: Размер по горизонтали

        :raise: ValueError
        """

        if not(isinstance(y, int) and 0 < y <= self.MAX_Y):
            raise ValueError(f'Размер по вертикали должен лежать в диапазоне 1-{self.MAX_Y}!')
        self._y: int = y

        if not(isinstance(x, int) and 0 < x <= self.MAX_X):
            raise ValueError(f'Размер по горизонтали должен лежать в диапазоне 1-{self.MAX_X}!')
        self._x: int = x

    @property
    def y(self) -> int:
        """
        Получить размер по вертикали
        """
        return self._y

    @property
    def x(self) -> int:
        """
        Получить размер по горизонтали.
        """
        return self._x

    @classmethod
    def parser(cls, line: str) -> 'SheetSize':
        """
        Разобрать размер листа

        :param line: Строка (в формате Y\tX)
        :raises ValueError:
        """

        error_text = f'Строка с размером листа должна быть в формате "<1-{cls.MAX_Y}>/t<1-{cls.MAX_X}>"!'

        if not (isinstance(line, str) and line):
            raise ValueError(error_text)

        values = line.split('\t')
        if not (len(values) == 2 and values[0].isdigit() and values[1].isdigit()):
            raise ValueError(error_text)

        return SheetSize(int(values[0]), int(values[1]))
