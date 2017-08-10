# coding: utf8

import pytest
from src.excel.cell.empty_value import *


class TestEmptyValue:
    @pytest.mark.parametrize('value', ['1', None, 0, 'None'])
    def test_1(self, value):
        """
        Не корректное создание экземпляра класса.
        :param value: Значение.
        """

        with pytest.raises(EmptyValue.ParseError):
            EmptyValue(value)

    @pytest.mark.parametrize('value', [''])
    def test_2(self, value):
        """
        Корректное создание экземпляра класса.
        :param str value: Значение.
        """

        assert EmptyValue(value).get_value() == value