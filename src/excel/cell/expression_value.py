"""
Тип ячейки 'Выражение'
"""

from collections import namedtuple
from typing import Tuple, Any, List, Union

from excel.cell.number_value import NumberValue
from excel.cell.ref_value import RefValue
from excel.cell.cell import CellValue


class ExpressionValue(CellValue):
    """
    Выражение.

    Начинается с символа =, может содержать:
        * Неотрицательные целые числа,
        * Ссылки на ячейки (одна латинска буква и следующа за ней цифра),
        * Простые арифметические выражения (+ - * /).
    Скобки запрещены. Все операции одинаково приоритетны.
    """

    def __init__(self, value: str):
        """
        :param value: Строка задающая значение
        :raise: ValueError
        """

        super().__init__()

        error_text = f'Значение "{value}" не является выражением!'

        if not (isinstance(value, str) and len(value) >= 1 and value[0] == '='):
            raise ValueError(error_text)

        if value[1:] == '':
            self._value = []
            return

        #
        # 1. Разбить строку с выражением на массив состоящий из операндов и операторов
        #
        expression = value[1:].upper()
        for o in _Operator.All:
            expression = expression.replace(o, f' {o} ')
        exp_str_list = expression.split()

        #
        # 2. Сформировать список операндов и операций выражений по массиву строкового представления
        #
        exp_item_list = []
        for v in exp_str_list:

            # Если элементом (выражения) является оператором, то последний элемент выражения должен быть операнд
            if v in _Operator.All:
                exp_item_list.append(v)
            else:
                operand = None

                for value_class in [NumberValue, RefValue]:
                    try:
                        operand = value_class(v)
                        break
                    except ValueError:
                        pass

                if operand:
                    exp_item_list.append(operand)
                else:
                    raise ValueError(error_text)

        #
        # 3. Валидация
        #

        # Кол-во элементов выражения должно быть не четным. Например 1+2+3
        if len(exp_item_list) % 2 != 1:
            raise ValueError(error_text)

        # Операторы в выражении должны быть быть строго в нечетных индексах списка. Например 1+2+3
        if not all(exp_item_list[i] in _Operator.All for i in range(1, len(exp_item_list), 2)):
            raise ValueError(error_text)

        # Операнды в выражении должны быть быть строго в четных индексах списка. Например 1+2+3
        if not all(isinstance(exp_item_list[i], (NumberValue, RefValue)) for i in range(0, len(exp_item_list), 2)):
            raise ValueError(error_text)

        self._value = exp_item_list

    def calc(self, cell_key: Tuple, sheet_cell_value: Any):
        """
        Расчитать выражение
        :param tuple cell_key: Ключ ячейки
        :param sheet_cell_value: Значения листа
        """

        _calc_exp_with_ref(cell_key, self.get_value(), sheet_cell_value)


class _Operator:
    """
    Операторы выражения
    """

    Plus = '+'
    """
    Плюс
    """

    Minus = '-'
    """
    Минус
    """

    Multiply = '*'
    """
    Умножить
    """

    Divide = '/'
    """
    Поделить
    """

    All = [Plus, Minus, Multiply, Divide]
    """
    Список всех операторов
    """

    @classmethod
    def exec(cls, operator: str, left_value: int, right_value: int) -> int:
        """
        Выполнить оператор.

            * Все вычисления выполняются с помощью целочисленной арифметики со знаком.

        :param operator: Оператор.
        :param left_value: Операнд.
        :param right_value: Операнд.

        :raise: _CalcExpError
        """

        if not (operator in cls.All and isinstance(left_value, int) and isinstance(right_value, int)):
            raise _CalcExpError.calc_exp()

        func = {
            cls.Plus: lambda a, b: a + b,
            cls.Minus: lambda a, b: a - b,
            cls.Multiply: lambda a, b: a * b,
            cls.Divide: lambda a, b: a / b
        }

        return int(func[operator](left_value, right_value))


class _CalcExpError(RuntimeError):
    """
    Ошибка вычисления выражения
    """

    @classmethod
    def calc_exp(cls) -> '_CalcExpError':
        """
        Ошибка выполнения выражения
        """
        return _CalcExpError('#CalcError')

    @classmethod
    def circle_ref(cls) -> '_CalcExpError':
        """
        Циклическая ссылка
        """
        return _CalcExpError('#CircleRef')

    @classmethod
    def not_valid_ref(cls) -> '_CalcExpError':
        """
        Некорректная ссылка
        """
        return _CalcExpError('#RefNotValid')


def _calc_exp_wo_ref(exp: List[str]) -> Union[int, str, None]:
    """
    Вычислить выражение без наличия ссылок (на ячейки).
    Вычисление происходит без рекурсии!

    * Все вычисления выполняются с помощью целочисленной арифметики со знаком
    * Операции над строками текста запрещены

    :param exp: Выражение
    :raise: _CalcExpError
    """

    if not (exp and isinstance(exp, list) and len(exp) % 2 == 1):
        raise _CalcExpError.calc_exp()

    # Выражение состоящие из одного элемента
    if len(exp) == 1 and (exp[0] is None or isinstance(exp[0], str)):
        return exp[0]

    result_exp: List[Union[str, int]] = exp
    while len(result_exp) > 1:
        operator = result_exp[1]
        operator_result = _Operator.exec(operator, result_exp[0], result_exp[2])

        del result_exp[0: 3]
        result_exp.insert(0, operator_result)

    return int(result_exp[0])


def _calc_exp_with_ref(cell_key: Tuple[int, int], exp: List, sheet_cell_value: dict):
    """
    Вычислить выражение.
    Вычисление происходит без рекурсии!

    :param cell_key: Координаты ячейки (x, y)
    :param exp: Элементы задающие выражения (см. ExpressionValue.get_value)
    :param sheet_cell_value: Текущие вычисленные значения листа
    """

    CellExp = namedtuple('CellExp', 'cell_key source_exp result_exp')
    CellExp.__doc__ = """
    Выражение ячейки
    
    :param tuple cell_key: Координаты ячейки (x, y)
    :param list source_exp: Исходное выражение
    :param list result_exp: Результирующее выражение
    """

    def process_cell_exp(cell_exp: CellExp) -> Union[CellExp, None]:
        """
        Обработать выражение ячейки

        :param cell_exp: Выражение ячейки
        :return: Очередное выражение для обработки
        """

        nonlocal sheet_cell_value

        # Обойти все элементы выражения
        while cell_exp.source_exp:
            exp_item = cell_exp.source_exp[0]

            if isinstance(exp_item, RefValue):
                ref_cell_key = exp_item.get_value()

                if ref_cell_key not in sheet_cell_value:
                    raise _CalcExpError.not_valid_ref()

                ref_value = sheet_cell_value[ref_cell_key]

                # Если выражение содержит другое выражение, то возвращаем его для последующего расчета
                if isinstance(ref_value, ExpressionValue):
                    return CellExp(ref_cell_key, ref_value.get_value(), [])

                exp_item_value = ref_value

            elif exp_item not in _Operator.All:
                exp_item_value = exp_item.get_value()

            else:
                exp_item_value = exp_item

            cell_exp.result_exp.append(exp_item_value)
            del cell_exp.source_exp[0]

        return None

    # Добавить выражение в стэк расчета
    process_exp_stack = [CellExp(cell_key, exp, [])]

    try:
        while process_exp_stack:
            process_exp = process_exp_stack[-1]
            next_process_exp = process_cell_exp(process_exp)

            # Если очередная обработка выражения приводит к необходимости нового вычисления,
            # то добавляем выражение для вычисления в стек расчета
            if next_process_exp:
                if any(e.cell_key == next_process_exp.cell_key for e in process_exp_stack):
                    raise _CalcExpError.circle_ref()

                process_exp_stack.append(next_process_exp)

            # Производим расчет
            else:
                sheet_cell_value[process_exp.cell_key] = _calc_exp_wo_ref(process_exp.result_exp)
                process_exp_stack.pop()

    except _CalcExpError as e:
        sheet_cell_value[process_exp_stack[-1].cell_key] = str(e)

        # В остальных, связанных ячейках по стэку, прописываем "Ошибка вычисления"
        error_text = str(_CalcExpError.calc_exp())
        for process_exp in process_exp_stack[0: -1]:
            sheet_cell_value[process_exp.cell_key] = error_text
