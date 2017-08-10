# coding: utf8

from excel.sheet import Sheet


def run():
    """
    Запустить утилиту.
    """

    size_line = input()
    sheet = Sheet(size_line)

    for y in range(0, sheet.get_size().y):
        sheet.add_line(input())

    result = sheet.calculate()
    print('\n')

    for y in range(0, sheet.get_size().y):
        print('\t'.join([str(result[(x + 1, y + 1)]) for x in range(0, sheet.get_size().x)]))

if __name__ == '__main__':
    run()
