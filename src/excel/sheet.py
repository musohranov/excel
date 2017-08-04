# coding: utf8

"""
Лист.
"""

from collections import namedtuple
from .cell import *


class Sheet:
    """
    Лист.
    """

    # Максимальные размеры листа расчитываются исходя из следующего утверждения
    # 'Ссылки на ячейки состоят из одной латинской буквы и следующей за ней цифры'.

    # Максимальный размер листа по горизонтали (A-Z)
    Max_Size_X = 26

    # Максимальный размер листа по вертикали (1-9)
    Max_Size_Y = 9

    class ParseError(ValueError):
        pass

    def __init__(self, line):
        """
        Конструктор.

        :param str line: Строка задающая размер листа.
        :raises Sheet.ParseError:
        """

        self._size_x, self._size_y = self._parser_size(line)
        self._cell_list = {}

    @classmethod
    def _parser_size(cls, line):
        """
        Разобрать строку с размером листа.

        :param str line: Строка.
        :rtype: (int, int)

        :raises Sheet.ParseError:
        """

        error_text = f'Строка с размером листа должна быть в формате "<Число 1>/t<Число 2>", ' \
                     f'где <Число> целое положительное!'

        if not (isinstance(line, str) and line):
            raise Sheet.ParseError(error_text)

        values = line.split('\t')
        if not (len(values) == 2 and values[0].isdigit() and values[1].isdigit()):
            raise Sheet.ParseError(error_text)

        size_y = int(values[0])
        size_x = int(values[1])

        if not(0 < size_x <= cls.Max_Size_X and
               0 < size_y <= cls.Max_Size_Y):
            raise Sheet.ParseError(error_text)

        return size_x, size_y

    def get_size(self):
        """
        Получить размер листа (x, y).
        :rtype: (int, int)
        """

        return self._size_x, self._size_y

    def parse_line(self, line):
        """
        Разобрать строку листа.

        :param str line: Строка со значениями в ячейках.
        :raises Sheet.ParseError:
        """

        if len(self._cell_list) == self._size_y * self._size_x:
            raise self.ParseError('Достигнут предел размерности таблицы по вертикали!')

        error_text = f'Строка со значением ячеек должна содержать ' \
                     f'"{self._size_x}" выражений разделенных символом табуляции!'

        if not isinstance(line, str):
            raise self.ParseError(error_text)

        cell_value_list = line.split('\t')
        if not (len(cell_value_list) == self._size_x):
            raise self.ParseError(error_text)

        # Заполнить текущую строку ячейками
        line_number = int(len(self._cell_list) / self._size_x) + 1
        for i, value in enumerate(cell_value_list):
            self._cell_list[(i + 1, line_number)] = Cell(value)

    def calculate(self):
        """
        Рассчитать значения.

        :rtype: dict
        :return Ключом является кортеж (x, y), значением вычисленное выражение.
        """

        if not (len(self._cell_list) == (self._size_x * self._size_y)):
            raise RuntimeError(f'Инициализация не закончена. '
                               f'Кол-во заданных ячеек "{len(self._cell_list)}" из "{self._size_x * self._size_y}"')

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

        :param tuple(int, int) cell_key: Координаты ячейки (x, y).
        :param list expression: Элементы задающие выражения (см. ExpressionValue.get_value).
        :param dict sheet_cell_value: Текущие вычисленные значения листа.
        """

        if not (isinstance(sheet_cell_value, dict) and len(sheet_cell_value) > 0):
            raise RuntimeError('Значения листа не должны быть пусты!')

        # Вычисление происходит без рекурсии!
        CellExp = namedtuple('CellExp', 'cell_key source_exp result_exp')

        # Стэк ячеек с выражениями (ключ ячейки, исходное выражения, выражение со значениями).
        cell_exp_stack = [CellExp(cell_key, list(expression), [])]

        # Пока стек выражений не пуст, обрабатываем.
        while cell_exp_stack:
            cell_exp = cell_exp_stack[-1]

            # Обработка выражения.
            while cell_exp.source_exp:
                item = cell_exp.source_exp[0]

                # Если элемент выражения не является ссылкой, добавляем элемент в результирующий список-выражение.
                if not isinstance(item, RefValue):
                    cell_exp.result_exp.append(item.get_value() if isinstance(item, NumberValue) else item)
                    del cell_exp.source_exp[0]
                    continue

                # Если ссылка указывает не на занчение, добавляем значение ссылки в результирующий список-выражение.
                # Иначе, выражение добавляем в стэк выражений необходимых для вычисления.

                ref_link = item.get_value()
                ref_value = sheet_cell_value[ref_link]

                if not isinstance(ref_value, ExpressionValue):
                    cell_exp.result_exp.append(ref_value)
                    del cell_exp.source_exp[0]
                else:
                    if any(exp.cell_key == ref_link for exp in cell_exp_stack):
                        # Циклическая ссылка! Для каждого элемента стэка расчета, прописать ошибку
                        for cell_exp in cell_exp_stack:
                            sheet_cell_value[cell_exp.cell_key] = Sheet._CalcError.Circle_Ref

                        return

                    cell_exp_stack.append(CellExp(ref_link, ref_value.get_value(), []))
                    break

            if not cell_exp.source_exp:
                # Обработка выражения закончена, вычислить результат.
                try:
                    result = ExpressionValue.calc(cell_exp.result_exp)
                except:
                    result = Sheet._CalcError.Calc
                sheet_cell_value[cell_exp.cell_key] = result

                cell_exp_stack.pop()
            else:
                # Приступить к обработке очередного выражения.
                pass
