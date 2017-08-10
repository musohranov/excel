# coding: utf8

import pytest

from src.excel.cell.number_value import NumberValue
from src.excel.cell.empty_value import EmptyValue
from src.excel.cell.text_value import TextValue
from src.excel.cell.expression_value import ExpressionValue

from src.excel.cell.cell import *


class TestParser:
    @pytest.mark.parametrize('value', ['-1',
                                       None,
                                       'Sample',
                                       '=X',
                                       1])
    def test_1(self, value):
        """
        Не корректное создание экземпляра класса.
        :param value: Значение.
        """

        with pytest.raises(ValueError):
            parser(value)

    @pytest.mark.parametrize('value', [('1', NumberValue),
                                       ('', EmptyValue),
                                       ("'Sample", TextValue),
                                       ('=1', ExpressionValue)])
    def test_1(self, value):
        """
        Корректное создание экземпляра класса.
        :param value: Значение.
        """

        assert isinstance(parser(value[0]), value[1])
