# coding: utf8

import re
from .value import Value


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
