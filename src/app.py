# coding: utf8

import sys
from excel.sheet import Sheet


def run():
    """
    Запустить утилиту.
    """

    try:
        size_line = input()
        sheet = Sheet(size_line)

        for y in range(0, sheet.get_size().y):
            sheet.add_line(input())

        result = sheet.calculate()

        for y in range(0, sheet.get_size().y):
            print('\n')
            print('\t'.join([str(result[(x + 1, y + 1)]) for x in range(0, sheet.get_size().x)]))

    except Exception as exp:
        print("Непредвиденная ошибка!")
        sys.exit()

if __name__ == '__main__':
    run()
