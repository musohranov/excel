"""
Утилита расчета 'таблицы' по типу excel.
Интерфейс пользователя реализован в виде командной строки.

В качестве первой строки ожидается значение в виде
Y \t X, где Y размер таблицы по вертикали, а X по горизонтали.

Ячейки последующий Y строк, должны быть размером X и значения разделены так же символом \t (табуляции).
"""

from excel.sheet import Sheet


def run():
    """
    Запустить приложение
    """

    size_line = input()
    sheet = Sheet(size_line)

    for y in range(0, sheet.get_size().y):
        sheet.add_line(input())

    result = sheet.calculate()

    for y in range(0, sheet.get_size().y):
        print('\t'.join([str(result[(x + 1, y + 1)]) for x in range(0, sheet.get_size().x)]))


if __name__ == '__main__':
    run()
