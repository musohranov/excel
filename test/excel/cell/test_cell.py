import pytest

from excel.cell.cell import CellValue
from excel.cell.empty_value import EmptyValue
from excel.cell.expression_value import ExpressionValue
from excel.cell.number_value import NumberValue
from excel.cell.text_value import TextValue


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
            CellValue.parser(value)

    @pytest.mark.parametrize('value', [('1', NumberValue),
                                       ('', EmptyValue),
                                       ("'Sample", TextValue),
                                       ('=1', ExpressionValue)])
    def test_1(self, value):
        """
        Корректное создание экземпляра класса.
        :param tuple value: Значение.
        """

        assert isinstance(CellValue.parser(value[0]), value[1])
