import pytest
from excel.cell.empty_value import EmptyValue


class TestEmptyValue:
    @pytest.mark.parametrize('value', ['1',
                                       None,
                                       0,
                                       'None'])
    def test_1(self, value):
        """
        Не корректное создание экземпляра класса.
        :param value: Значение.
        """

        with pytest.raises(ValueError):
            EmptyValue(value)

    @pytest.mark.parametrize('value', [''])
    def test_2(self, value):
        """
        Корректное создание экземпляра класса.
        :param str value: Значение.
        """

        assert EmptyValue(value).get_value() == value
