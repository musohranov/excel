# coding: utf8

"""
Парсер ячейки.
"""

import re

__all__ = ['Cell', 'EmptyValue', 'NumberValue', 'TextValue', 'ExpressionValue', 'RefValue']


class Cell:
    """
    Парсер ячейки.
    """

    class ParseError(ValueError):
        pass

    def __init__(self, value):
        """
        Конструктор.

        :param str value: Строка задающая значение ячейки.
        :raises Cell.ParseError:
        """

        self._value = None
        for value_class in [EmptyValue, NumberValue, TextValue, ExpressionValue]:
            try:
                self._value = value_class(value)
                break
            except ValueError:
                pass

        # Если значению не соответствует ни один тип.
        if not self._value:
            raise Cell.ParseError(f'Значение "{value}" не соответствует ни одному типу!')

    def get_value(self):
        """
        Получить значение.
        :rtype: Value
        """

        return self._value


class Value:
    """
    Значение.
    """

    class ParseError(ValueError):
        pass

    def __init__(self):
        """
        Конструктор.
        """

        self._value = None

    def get_value(self):
        """
        Получить занчение.
        """

        return self._value


class EmptyValue(Value):
    """
    Пустое значение.
    """

    def __init__(self, value):
        """
        Конструктор.

        :param str value: Строка задающая значение.
        :raises Value.ParseError:
        """

        super().__init__()

        if not (isinstance(value, str) and value == ''):
            raise self.ParseError(f'Значение "{value}" не является пустым!')

        self._value = value


class NumberValue(Value):
    """
    Число.

    Целое положительное.
    """

    def __init__(self, value):
        """
        Конструктор.

        :param str value: Строка задающая значение.
        :raises Value.ParseError:
        """

        super().__init__()

        if isinstance(value, str) and value.isdigit() and int(value) >= 0:
            self._value = int(value)
        else:
            raise self.ParseError(f'Значение "{value}" не является целым положительным числом!')


class TextValue(Value):
    """
    Текст.

    Начинается с символа '
    """

    def __init__(self, value):
        """
        Конструктор.

        :param str value: Строка задающая значение.
        :raises Value.ParseError:
        """

        super().__init__()

        if isinstance(value, str) and len(value) > 0 and value[0] == "'":
            self._value = value[1:]
        else:
            raise self.ParseError(f'Значение "{value}" не является текстом!')


class RefValue(Value):
    """
    Ссылка.

    Одна латинска буква и следующа за ней цифра.
    """

    def __init__(self, value):
        """
        Конструктор.

        :param str value: Строка задающая значение.
        :raises Value.ParseError:
        """

        super().__init__()

        if isinstance(value, str) and len(value) == 2 \
                and re.search(r'[A-Z]', value[0].upper()) is not None and value[1].isdigit() and int(value[1]) > 0:
            self._value = value.upper()
        else:
            raise self.ParseError(f'Значение "{value}" не является ссылкой!')

    def get_value(self):
        """
        Получить значение.

        Преобразует значение ссылки в формате (x, y)
        :rtype: tuple(int, int)
        """

        return ord(self._value[0]) - ord('A') + 1, int(self._value[1])


class ExpressionValue(Value):
    """
    Выражение.

    Начинается с символа =, может содержать:
        * Неотрицательные целые числа,
        * Ссылки на ячейки (одна латинска буква и следующа за ней цифра),
        * Простые арифметические выражения (+ - * /).
    Скобки запрещены. Все операции одинаково приоритетны.
    """

    class Operator:
        """
        Операторы.
        """

        # Плюс
        Plus = '+'

        # Минус
        Minus = '-'

        # Умножить
        Multiply = '*'

        # Делить
        Divide = '/'

        # Все операторы
        All = [Plus, Minus, Multiply, Divide]

    def __init__(self, value):
        """
        Конструктор.

        :param str value: Строка задающая значение.
        :raises Value.ParseError:
        """

        super().__init__()

        # Базовая проверка
        if not (isinstance(value, str) and len(value) >= 1 and value[0] == '='):
            raise self.ParseError(f'Значение "{value}" не является выражением!')

        if value[1:] == '':
            self._value = []
            return

        # Проверка на присутствие только корректных символов
        if re.search(r'[^A-Z0-9+\-*/]', value[1:].upper()):
            raise self.ParseError(f'Выражение "{value}" содержит не корректные символы!')

        # Разбить выражение на массив состоящий из операндов и операторов
        value_list_ = value[1:].upper()
        for o in self.Operator.All:
            value_list_ = value_list_.replace(o, f' {o} ')

        expression = value_list_.split()

        # Сформировать список операндов и операций
        value_list = []
        for v in expression:

            # Если элементом (выражения) является оператором, то последний элемент выражения должен быть операнд
            if v in self.Operator.All:
                if len(value_list) > 0 and value_list[-1] not in self.Operator.All:
                    value_list.append(v)
                else:
                    raise self.ParseError(f'Значение "{value}" не является выражением!')
            else:
                operand = None
                for value_class in [NumberValue, RefValue]:
                    try:
                        operand = value_class(v)
                        break
                    except self.ParseError:
                        pass

                # Если элементом (выражения) является операнд, то он должен быть числом либо ссылкой и предыдущий
                # элемент должен быть оператором
                if operand and (len(value_list) == 0 or value_list[-1] in self.Operator.All):
                    value_list.append(operand)
                else:
                    raise self.ParseError(f'Значение "{value}" не является выражением!')

        # Если выражение не пусто, то последний элемент должен быть строго операнд
        if not (len(value_list) > 0 and isinstance(value_list[-1], (NumberValue, RefValue))):
            raise self.ParseError(f'Значение "{value}" не является выражением!')

        self._value = value_list

    class CalcError(RuntimeError):
        pass

    @classmethod
    def calc(cls, expression):
        """
        Вычислить выражение.

        :param list expression: Выражение.
        :rtype: int|str|None

        :raises Value.ParseError:
        """

        if not (expression is not None and isinstance(expression, list) and len(expression) > 0):
            raise cls.CalcError('Список не задает корректное выражение!')

        # Кол-во элементов в выражении должно быть нечетным. Например 1, или 1+2
        if not len(expression) % 2:
            raise cls.CalcError('Список не задает корректное выражение!')

        # Выражение состоящие из одного элемента
        if len(expression) == 1 and (expression[0] is None or isinstance(expression[0], str)):
            return expression[0]

        # Операторы в выражении должны быть быть строго в нечетных индексах списка. Например 1+2+3
        if not all(expression[i] in cls.Operator.All for i in range(1, len(expression), 2)):
            raise cls.CalcError('Список не задает корректное выражение!')

        # Операнды в выражении должны быть быть строго в четных индексах списка. Например 1+2+3
        if not all(isinstance(expression[i], int) for i in range(0, len(expression), 2)):
            raise cls.CalcError('Список не задает корректное выражение!')

        # Вычислить результат выражения.from
        result_list = expression
        while len(result_list) > 1:
            operator = result_list[1]

            try:
                if operator == cls.Operator.Plus:
                    operator_result = result_list[0] + result_list[2]

                elif operator == cls.Operator.Minus:
                    operator_result = result_list[0] - result_list[2]

                elif operator == cls.Operator.Divide:
                    operator_result = int(result_list[0] / result_list[2])

                elif operator == cls.Operator.Multiply:
                    operator_result = result_list[0] * result_list[2]

                else:
                    raise RuntimeError()
            except:
                raise cls.CalcError('Ошибка вычисления!')

            del result_list[0: 3]
            result_list.insert(0, operator_result)

        return result_list[0]