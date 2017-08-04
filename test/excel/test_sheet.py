# coding: utf8

import pytest

from src.excel.cell import *
from src.excel.sheet import *


class TestSheetConstructor:
    @pytest.mark.parametrize('line', [0, '', None])
    def test_1(self, line):
        """
        Не корректное создание экземпляра класса.
        :param str line: Строка задающая размер листа.
        """

        with pytest.raises(Sheet.ParseError):
            Sheet(line)

    @pytest.mark.parametrize('line', ['1',
                                      '1 2',
                                      '1\t\t2',
                                      '1\t2\t',
                                      ' 1\t2',
                                      '1\t 2',
                                      '1\t2 ',
                                      '1.1\t2',
                                      '1\t2.2'
                                      ])
    def test_2(self, line):
        """
        Не корректное создание экземпляра класса.
        :param str line: Строка задающая размер листа.
        """

        with pytest.raises(Sheet.ParseError):
            Sheet(line)

    @pytest.mark.parametrize('line', ['1',
                                      '0\t0',
                                      '0\t2',
                                      '2\t0',
                                      '-1\t2',
                                      '1\t-2',
                                      '1025\t2',
                                      '1\t1025'
                                      ])
    def test_3(self, line):
        """
        Не корректное создание экземпляра класса.
        :param str line: Строка задающая размер листа.
        """

        with pytest.raises(Sheet.ParseError):
            Sheet(line)

    @pytest.mark.parametrize('size_x', [1, Sheet.Max_Size_X])
    @pytest.mark.parametrize('size_y', [1, Sheet.Max_Size_Y])
    def test_4(self, size_x, size_y):
        """
        Корректное создание экземпляра класса.
        :param int size_x: Размер листа.
        :param int size_y: Размер листа.
        """

        assert Sheet(f'{size_y}\t{size_x}').get_size() == (size_x, size_y)


class TestSheetParseLine:
    @pytest.mark.parametrize('line', [['1', '0'],
                                      ['1\t0']])
    def test_1(self, line):
        """
        Не корректное добавление строк.
        :param line: Строка.
        """

        sheet = Sheet('1\t1')
        for l in line[:-1]:
            sheet.parse_line(l)

        with pytest.raises(ValueError):
            sheet.parse_line(line[-1])

    @pytest.mark.parametrize('line', [None,
                                      1, -1, 0])
    def test_2(self, line):
        """
        Не корректное добавление строк.
        :param line: Строка.
        """

        sheet = Sheet('1\t1')
        with pytest.raises(Sheet.ParseError):
            sheet.parse_line(line)

    def test_3(self):
        """
        Корректное добавление строк.
        """

        sheet = Sheet('2\t1')

        sheet.parse_line('')
        assert len(sheet._cell_list) == 1
        assert isinstance(sheet._cell_list[(1, 1)], Cell)

        sheet.parse_line('')
        assert len(sheet._cell_list) == 2
        assert isinstance(sheet._cell_list[(1, 2)], Cell)


class TestSheetCalculate:
    def test_1(self):
        """
        Не корректная иницализация.
        """

        sheet = Sheet('2\t1')

        with pytest.raises(RuntimeError):
            sheet.calculate()

        sheet.parse_line('')
        with pytest.raises(RuntimeError):
            sheet.calculate()

    @pytest.mark.parametrize('size_y', [1, 2, Sheet.Max_Size_Y])
    def test_2(self, size_y):
        """
        Циклическое вычисление.
        :param int size_y: Размерность по вертикали. Вложенность расчета выражения.
        """

        sheet = Sheet(f'{size_y}\t{2}')
        for y in range(1, size_y):
            sheet.parse_line(f'=A{y + 1}\t1')

        # Добавили цикличность
        sheet.parse_line(f'=A1\t1')

        result = sheet.calculate()
        for y in range(1, size_y + 1):
            assert result[(1, y)] == Sheet._CalcError.Circle_Ref
            assert result[(2, y)] == 1

    def test_3(self):
        """
        Максимальная циклическая вложенность\зависимость. =A2, =A3, ..., =Z8, =A1
        """

        sheet = Sheet(f'{Sheet.Max_Size_Y}\t{Sheet.Max_Size_X}')
        for y in range(1, sheet.get_size()[1] + 1):
            line = [f'={chr(ord("A") + x)}{y}' for x in range(1, sheet.get_size()[0])]

            # Добавить цикличность
            line.append('=A1' if y == Sheet.Max_Size_Y else f'=A{y + 1}')

            sheet.parse_line('\t'.join(line))

        result = sheet.calculate()
        for y in range(1, sheet.get_size()[1] + 1):
            for x in range(1, sheet.get_size()[0] + 1):
                assert result[(x, y)] == Sheet._CalcError.Circle_Ref

    def test_4(self):
        """
        Максимальное циклическое вычисление. =A2 + 1, =A3 + 1, ..., =Z8 + 1, =1
        """

        sheet = Sheet(f'{Sheet.Max_Size_Y}\t{Sheet.Max_Size_X}')
        for y in range(1, sheet.get_size()[1] + 1):
            line = [f'={chr(ord("A") + x)}{y}+1' for x in range(1, sheet.get_size()[0])]
            line.append('=1' if y == sheet.get_size()[1] else f'=A{y + 1}+1')

            sheet.parse_line('\t'.join(line))

        result = sheet.calculate()
        for y in range(1, sheet.get_size()[1] + 1):
            for x in range(1, sheet.get_size()[0] + 1):
                assert result[(x, y)] == (sheet.get_size()[0] * sheet.get_size()[1] - sheet.get_size()[0] * (y - 1) - x + 1)

    def test_5(self):
        """
        Общее успешное вычисление. С ошибками, с зацикливанием, со всеми видами типов.
        """

        sheet = Sheet('3\t3')
        sheet.parse_line("=A1\t=3-1*2+1\t'Sample")
        sheet.parse_line("=C1\t=A2-7/2\t=B1-8/2")
        sheet.parse_line("'\t=A3\t=B3")

        result = sheet.calculate()

        assert result[(1, 1)] == Sheet._CalcError.Circle_Ref
        assert result[(2, 1)] == 5
        assert result[(3, 1)] == 'Sample'

        assert result[(1, 2)] == 'Sample'
        assert result[(2, 2)] == Sheet._CalcError.Calc
        assert result[(3, 2)] == -1

        assert result[(1, 3)] == ''
        assert result[(2, 3)] == ''
        assert result[(3, 3)] == ''
