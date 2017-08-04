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

        for j in range(0, sheet.get_size()[1]):
            line = input()
            sheet.parse_line(line)

        result = sheet.calculate()

        for y in range(0, sheet.get_size()[1]):
            print('\n')
            print('\t'.join([str(result[(x + 1, y + 1)]) for x in range(0, sheet.get_size()[0])]))

    except Exception as exp:
        print(exp)
        sys.exit()

if __name__ == '__main__':
    run()
