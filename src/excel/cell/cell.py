# coding: utf8

from .value import Value
from .empty_value import EmptyValue
from .number_value import NumberValue
from .text_value import TextValue
from .expression_value import ExpressionValue


def parser(value):
    """
    Разобрать значение ячейки.

    :param str value: Значение ячейки.
    :rtype: Value
    :raises ValueError:
    """

    for value_class in [EmptyValue, NumberValue, TextValue, ExpressionValue]:
        try:
            return value_class(value)
        except ValueError:
            pass

    raise ValueError(f'Значение "{value}" не соответствует ни одному типу!')
