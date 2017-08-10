# coding: utf8

from .value import Value


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
