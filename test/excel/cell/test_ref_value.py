# coding: utf8

import pytest
from src.excel.cell.ref_value import RefValue


class TestRefValue:
    @pytest.mark.parametrize('value', ['A0',
                                       None,
                                       0,
                                       '1A',
                                       '',
                                       'A11'])
    def test_1(self, value):
        """
        Не корректное создание экземпляра класса.
        :param value: Значение.
        """

        with pytest.raises(ValueError):
            RefValue(value)

    @pytest.mark.parametrize('value', [('A1', (1, 1)),
                                       ('z9', (26, 9))])
    def test_2(self, value):
        """
        Корректное создание экземпляра класса.
        :param tuple value: Значение.
        """

        assert RefValue(value[0]).get_value() == value[1]
