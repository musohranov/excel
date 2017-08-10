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
        :raises ValueError:
        """

        super().__init__()

        if not (isinstance(value, str) and value.isdigit() and int(value) >= 0):
            raise ValueError(f'Значение "{value}" не является целым положительным числом!')

        self._value = int(value)
