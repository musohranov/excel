# coding: utf8

import pytest

from src.excel.cell.number_value import NumberValue
from src.excel.cell.ref_value import RefValue

from src.excel.cell.expression_value import *


class TestExpressionValue:
    @pytest.mark.parametrize('value', ['', 'a9', 'None',
                                       '1', '10000', '0',
                                       '=-1', '=+', '=-', '=*', '=/',
                                       '==', '=1+', '=1+A+2', '=Z*1'
                                       ])
    def test_1(self, value):
        """
        Не корректное создание экземпляра класса.
        :param value: Значение.
        """

        with pytest.raises(ExpressionValue.ParseError):
            ExpressionValue(value)

    def test_2(self):
        """
        Корректное создание экземпляра класса.
        """

        assert ExpressionValue('=').get_value() == []

    @pytest.mark.parametrize('value', [('=1', NumberValue, 1),
                                       ('=10000', NumberValue, 10000),
                                       ('=0', NumberValue, 0),
                                       ('=a9', RefValue, (1, 9))
                                       ])
    def test_3(self, value):
        """
        Корректное создание экземпляра класса.
        :param tuple value: Значение.
        """

        result_value = ExpressionValue(value[0]).get_value()[0]
        assert isinstance(result_value, value[1]) and result_value.get_value() == value[2]

    @pytest.mark.parametrize('o_1', ['100', 'A1'])
    @pytest.mark.parametrize('o_2', ['+', '-', '*', '/'])
    @pytest.mark.parametrize('o_3', ['2', 'z9'])
    @pytest.mark.parametrize('o_4', ['+', '-', '*', '/'])
    @pytest.mark.parametrize('o_5', ['0', 'b3'])
    @pytest.mark.parametrize('o_len', [3, 5])
    def test_4(self, o_1, o_2, o_3, o_4, o_5, o_len):
        """
        Корректное создание экземпляра класса.
        """

        ExpressionValue('=' + ''.join([o_1, o_2, o_3, o_4, o_5][:o_len]))

        # Проверить выражение которое заведомо оканчивается на оператор
        with pytest.raises(ValueError):
            ExpressionValue('=' + ''.join([o_1, o_2, o_3, o_4, o_5][:o_len - 1]))


class TestExpressionValueCalc:
    @pytest.mark.parametrize('value', ['',
                                       None,
                                       'Text',
                                       "'Text",
                                       1,
                                       [1, '+'],
                                       [1, 2, '-'],
                                       ['*', 1, 2],
                                       [1, '+', '0']])
    def test_1(self, value):
        """
        Не корректное выражение.
        :param value: Значение.
        """

        with pytest.raises(ExpressionValue.CalcError):
            ExpressionValue.calc(value)

    @pytest.mark.parametrize('value', [([None], None),
                                       (['1'], '1'),
                                       ([''], ''),
                                       ([1], 1),
                                       ([-1], -1),
                                       ([1, '+', 2], 3),
                                       ([1, '+', -2], -1),
                                       ([1, '-', 2], -1),
                                       ([1, '-', -2], 3),
                                       ([1, '*', 2], 2),
                                       ([1, '*', -2], -2),
                                       ([4, '/', 2], 2),
                                       ([5, '/', 3], 1),
                                       ([11, '/', 4], 2),
                                       ([1, '/', 2], 0),
                                       ([4, '*', -2], -8),
                                       ([5, '-', 2, '+', 1, '*', 3, '/', 2], 6)])
    def test_2(self, value):
        """
        Корректное выражение.
        :param value: Значение.
        """

        assert ExpressionValue.calc(value[0]) == value[1]