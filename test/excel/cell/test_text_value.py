import pytest
from excel.cell.text_value import TextValue


class TestTextValue:
    @pytest.mark.parametrize('value', ['abc',
                                       None,
                                       0,
                                       ''])
    def test_1(self, value):
        """
        Не корректное создание экземпляра класса.
        :param value: Значение.
        """

        with pytest.raises(ValueError):
            TextValue(value)

    @pytest.mark.parametrize('value', ["'",
                                       "''",
                                       "'1",
                                       "'1'",
                                       "'abc",
                                       "'None",
                                       "'0"])
    def test_2(self, value):
        """
        Корректное создание экземпляра класса.
        :param str value: Значение.
        """

        assert TextValue(value).get_value() == value[1:]
