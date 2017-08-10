# coding: utf8

from .value import Value


class EmptyValue(Value):
    """
    Пустое значение.
    """

    def __init__(self, value):
        """
        Конструктор.

        :param str value: Строка задающая значение.
        :raises ValueError:
        """

        super().__init__()

        if not (isinstance(value, str) and value == ''):
            raise ValueError(f'Значение "{value}" не является пустым!')

        self._value = value
