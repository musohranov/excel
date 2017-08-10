# coding: utf8


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
