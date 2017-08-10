# coding: utf8

from .value import Value
from .empty_value import EmptyValue
from .number_value import NumberValue
from .text_value import TextValue
from .expression_value import ExpressionValue


class Cell:
    """
    Ячейка.
    """

    class ParseError(ValueError):
        pass

    def __init__(self, value):
        """
        Конструктор.

        :param str value: Строка задающая значение ячейки.
        :raises ValueError:
        """

        self._value = None
        for value_class in [EmptyValue, NumberValue, TextValue, ExpressionValue]:
            try:
                self._value = value_class(value)
                break
            except ValueError:
                pass

        if not self._value:
            raise ValueError(f'Значение "{value}" не соответствует ни одному типу!')

    def get_value(self):
        """
        Получить значение.
        :rtype: Value
        """

        return self._value
