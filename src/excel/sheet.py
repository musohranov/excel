# coding: utf8

"""
Лист.
"""

from collections import namedtuple

from .cell.cell import Cell
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
            self._cell_list[(i + 1, line_number)] = Cell(value)

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
            cell_value = cell_value.get_value()
            sheet_cell_value[key] = \
                cell_value.get_value() if not isinstance(cell_value, ExpressionValue) else cell_value

        # Вычислить результат для всех выражений.
        for key, cell_value in sheet_cell_value.items():
            if isinstance(cell_value, ExpressionValue):
                Sheet._calc_expression(key, cell_value.get_value(), sheet_cell_value)

        return sheet_cell_value

    class _CalcError:
        # Циклическая ссылка
        Circle_Ref = '#CircRef'

        # Ошибка вычисления
        Calc = '#Calc'

    @staticmethod
    def _calc_expression(cell_key, expression, sheet_cell_value):
        """
        Вычислить выражение.
        Вычисление происходит без рекурсии!

        :param tuple(int, int) cell_key: Координаты ячейки (x, y).
        :param list expression: Элементы задающие выражения (см. ExpressionValue.get_value).
        :param dict sheet_cell_value: Текущие вычисленные значения листа.
        """

        CellExp = namedtuple('CellExp', 'cell_key source_exp result_exp')

        class CircleRefError(RuntimeError):
            pass

        # 1. Добавить выражение в стэк для очередного расчета
        process_exp_stack = [CellExp(cell_key, expression, [])]

        try:
            while process_exp_stack:
                cell_exp = process_exp_stack[-1]

                # 2. Обработка выражения.
                # Обойти все элементы выражения и если встречаем ссылку, то перейти к расчету этого выражения
                while cell_exp.source_exp:
                    exp_item = cell_exp.source_exp[0]

                    if isinstance(exp_item, RefValue):
                        ref_cell_key = exp_item.get_value()

                        # Проверка на цикличность.
                        if any(exp.cell_key == ref_cell_key for exp in process_exp_stack):
                            raise CircleRefError()

                        ref_value = sheet_cell_value.get(ref_cell_key, Sheet._CalcError.Calc)

                        # Значения ячейки по указанной ссылки содержит выражение.
                        # Выражение помещаем в стек для вычислений
                        if isinstance(ref_value, ExpressionValue):
                            process_exp_stack.append(CellExp(ref_cell_key, ref_value.get_value(), []))
                            break

                        item_value = ref_value

                    else:
                        item_value = exp_item.get_value() if not exp_item in ExpressionValue.Operator.All else exp_item

                    cell_exp.result_exp.append(item_value)
                    del cell_exp.source_exp[0]

                # 3. Выражение более не содержит ссылок на другие ячейки, можно приступать к вычислению.
                if not cell_exp.source_exp:
                    try:
                        result = ExpressionValue.calc(cell_exp.result_exp)
                    except:
                        result = Sheet._CalcError.Calc
                    sheet_cell_value[cell_exp.cell_key] = result

                    process_exp_stack.pop()
                else:
                    # Приступить к обработке очередного выражения.
                    pass
        except CircleRefError:
            # Циклическая ссылка! Для каждого элемента стэка расчета, прописать ошибку
            for cell_exp in process_exp_stack:
                sheet_cell_value[cell_exp.cell_key] = Sheet._CalcError.Circle_Ref


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
        Разобрать строку.
        Строка в формате Y\tX

        :param str line: Строка.
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
