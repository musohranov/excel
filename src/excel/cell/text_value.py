# coding: utf8

from .value import Value


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
