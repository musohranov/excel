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
        :raises ValueError:
        """

        super().__init__()

        if not (isinstance(value, str) and len(value) > 0 and value[0] == "'"):
            raise ValueError(f'Значение "{value}" не является текстом!')

        self._value = value[1:]
