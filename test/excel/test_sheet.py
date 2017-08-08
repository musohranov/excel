# coding: utf8

import pytest

from src.excel.cell import *
from src.excel.sheet import *


class TestSheetConstructor:
    """
    Конструктор.
    """

    def test_1(self):
        """
        Создание экземпляра класса.
        """

        assert isinstance(Sheet('1\t1').get_size(), SheetSize)


class TestSheetAddLine:
    """
    Добавить строку.
    """

    @pytest.mark.parametrize('line', [None,
                                      1,
                                      -1,
                                      0])
    def test_1(self, line):
        """
        Не корректное добавление строк.
        :param line: Строка.
        """

        sheet = Sheet('1\t1')
        with pytest.raises(ValueError):
            sheet.add_line(line)

    @pytest.mark.parametrize('line', [['1', '0'],
                                      ['1\t0']])
    def test_2(self, line):
        """
        Не корректное добавление строк.
        :param line: Строка.
        """

        sheet = Sheet('1\t1')
        for l in line[:-1]:
            sheet.add_line(l)

        with pytest.raises(ValueError):
            sheet.add_line(line[-1])

    def test_3(self):
        """
        Корректное добавление строк.
        """

        sheet = Sheet('2\t1')

        sheet.add_line('')
        assert len(sheet._cell_list) == 1
        assert isinstance(sheet._cell_list[(1, 1)], Cell)

        sheet.add_line('')
        assert len(sheet._cell_list) == 2
        assert isinstance(sheet._cell_list[(1, 2)], Cell)


class TestSheetCalculate:
    """
    Рассчитать значения.
    """

    def test_1(self):
        """
        Преждевременный вызов.
        """

        sheet = Sheet('2\t1')

        with pytest.raises(RuntimeError):
            sheet.calculate()

        sheet.add_line('')
        with pytest.raises(RuntimeError):
            sheet.calculate()

    @pytest.mark.parametrize('size_y', [1, 2, SheetSize.Max_Y])
    def test_2(self, size_y):
        """
        Циклическое вычисление.
        :param int size_y: Размерность по вертикали. Вложенность расчета выражения.
        """

        sheet = Sheet(f'{size_y}\t{2}')
        for y in range(1, size_y):
            sheet.add_line(f'=A{y + 1}\t1')

        # Добавили цикличность
        sheet.add_line(f'=A1\t1')

        result = sheet.calculate()
        for y in range(1, size_y + 1):
            assert result[(1, y)] == Sheet._CalcError.Circle_Ref
            assert result[(2, y)] == 1

    def test_3(self):
        """
        Максимальная циклическая вложенность\зависимость. =A2, =A3, ..., =Z8, =A1
        """

        sheet = Sheet(f'{SheetSize.Max_Y}\t{SheetSize.Max_X}')
        for y in range(1, sheet.get_size().y + 1):
            line = [f'={chr(ord("A") + x)}{y}' for x in range(1, sheet.get_size().x)]

            # Добавить цикличность
            line.append('=A1' if y == SheetSize.Max_Y else f'=A{y + 1}')

            sheet.add_line('\t'.join(line))

        result = sheet.calculate()
        for y in range(1, sheet.get_size().y + 1):
            for x in range(1, sheet.get_size().x + 1):
                assert result[(x, y)] == Sheet._CalcError.Circle_Ref

    def test_4(self):
        """
        Максимальное циклическое вычисление. =A2 + 1, =A3 + 1, ..., =Z8 + 1, =1
        """

        sheet = Sheet(f'{SheetSize.Max_Y}\t{SheetSize.Max_X}')
        for y in range(1, sheet.get_size().y + 1):
            line = [f'={chr(ord("A") + x)}{y}+1' for x in range(1, sheet.get_size().x)]

            # Замыкаем вычисление
            line.append('=1' if y == sheet.get_size().y else f'=A{y + 1}+1')

            sheet.add_line('\t'.join(line))

        result = sheet.calculate()
        for y in range(1, sheet.get_size().y + 1):
            for x in range(1, sheet.get_size().x + 1):
                assert result[(x, y)] == \
                       (sheet.get_size().y * sheet.get_size().x - sheet.get_size().x * (y - 1) - x + 1)

    def test_5(self):
        """
        Вычисление с не корректной ссылкой.
        """

        sheet = Sheet('1\t1')
        sheet.add_line('=B1')

        result = sheet.calculate()
        assert result[(1, 1)] == Sheet._CalcError.Calc

    def test_6(self):
        """
        Общее успешное вычисление. С ошибками, с зацикливанием, со всеми видами типов.
        """

        sheet = Sheet('3\t3')
        sheet.add_line("=A1\t=3-1*2+1\t'Sample")
        sheet.add_line("=C1\t=A2-7/2\t=B1-8/2")
        sheet.add_line("'\t=A3\t=B4")

        result = sheet.calculate()

        assert result[(1, 1)] == Sheet._CalcError.Circle_Ref
        assert result[(2, 1)] == 5
        assert result[(3, 1)] == 'Sample'

        assert result[(1, 2)] == 'Sample'
        assert result[(2, 2)] == Sheet._CalcError.Calc
        assert result[(3, 2)] == -1

        assert result[(1, 3)] == ''
        assert result[(2, 3)] == ''
        assert result[(3, 3)] == Sheet._CalcError.Calc


class TestSheetSizeConstructor:
    """
    Конструктор.
    """

    @pytest.mark.parametrize('size', [(None, None), ('', ''),
                                      (1, 'a'), ('a', 1),
                                      ('1', 1), (1, '1'),
                                      ('1', None), (None, '1'),
                                      (-1, 1), (1, -1),
                                      (0, 1), (1, 0),
                                      (1, SheetSize.Max_X + 1), (SheetSize.Max_Y + 1, 1),
                                      (1.1, 1), (1, 1.1)])
    def test_1(self, size):
        """
        Не корректное создание экземпляра класса.
        :param tuple size: Размер листа.
        """

        with pytest.raises(ValueError):
            SheetSize(size[0], size[1])

    @pytest.mark.parametrize('size_y', [1, SheetSize.Max_Y])
    @pytest.mark.parametrize('size_x', [1, SheetSize.Max_X])
    def test_2(self, size_y, size_x):
        """
        Корректное создание экземпляра класса.
        :param int size_y: Размер по вертикали.
        :param int size_x: Размер по горизонтали.
        """

        sheet_size = SheetSize(size_y, size_x)
        assert sheet_size.y == size_y
        assert sheet_size.x == size_x


class TestSheetSizeParser:
    """
    Разбор.
    """

    @pytest.mark.parametrize('line', [0,
                                      '',
                                      None,
                                      '1',
                                      '1 1',
                                      '1\t\t1',
                                      '1\t1\t',
                                      ' 1\t1',
                                      '1\t 1',
                                      '1\t1 ',
                                      '1.1\t1',
                                      '1\t1.1'
                                      ])
    def test_1(self, line):
        """
        Не корректный разбор.
        :param line: Строка.
        """

        with pytest.raises(ValueError):
            SheetSize.parser(line)

    @pytest.mark.parametrize('size_y', [1, SheetSize.Max_Y])
    @pytest.mark.parametrize('size_x', [1, SheetSize.Max_X])
    def test_2(self, size_y, size_x):
        """
        Корректный разбор.
        :param int size_y: Размер по вертикали.
        :param int size_x: Размер по горизонтали.
        """

        SheetSize.parser(f'{size_y}\t{size_x}')
