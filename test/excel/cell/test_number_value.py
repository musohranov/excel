# coding: utf8

import pytest
from src.excel.cell.number_value import *


class TestNumberValue:
    @pytest.mark.parametrize('value', ['-1',
                                       '1.1',
                                       '1.0',
                                       None,
                                       1,
                                       1.5,
                                       -1])
    def test_1(self, value):
        """
        Не корректное создание экземпляра класса.
        :param value: Значение.
        """

        with pytest.raises(ValueError):
            NumberValue(value)

    @pytest.mark.parametrize('value', ['1', '0'])
    def test_2(self, value):
        """
        Корректное создание экземпляра класса.
        :param str value: Значение.
        """

        assert NumberValue(value).get_value() == int(value)
