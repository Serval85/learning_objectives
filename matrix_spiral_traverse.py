 Тестовое задание по python
# Условие
# Необходимо реализовать Python-библиотеку, которая осуществляет получение квадратной матрицы (NxN) и возвращает её пользователю в виде List[int].
# Этот список должен содержать результат обхода полученной матрицы по спирали: против часовой стрелки, начиная с левого верхнего угла (см. test case ниже).
#
# Пример исходной матрицы:
# +-----+-----+-----+-----+
# |  10 |  20 |  30 |  40 |
# +-----+-----+-----+-----+
# |  50 |  60 |  70 |  80 |
# +-----+-----+-----+-----+
# |  90 | 100 | 110 | 120 |
# +-----+-----+-----+-----+
# | 130 | 140 | 150 | 160 |
# +-----+-----+-----+-----+
# Матрица гарантированно содержит целые неотрицательные числа. Форматирование границ иными символами не предполагается.
# Требования к выполнению и оформлению
# Библиотека содержит функцию со следующим интерфейсом:
# def get_matrix(filename: str) -> List[int]:
#     ...
# Функция единственным аргументом получает имя файла содержащего матрицу.
# Функция возвращает список, содержащий результат обхода полученной матрицы по спирали: против часовой стрелки, начиная с левого верхнего угла.
# В дальнейшем размерность матрицы может быть изменена с сохранением форматирования.
# Код должен сохранить свою работоспособность на квадратных матрицах другой размерности.

from typing import List

def read_matrix_from_file(filename: str) -> List[List[int]]:
    """
    Читает матрицу из файла.

    Args:
        filename (str): Имя файла, содержащего матрицу.

    Returns:
        List[List[int]]: Двумерная матрица целых чисел.
    """
    matrix = []
    with open(filename, 'r') as file:
        for line in file:
            if not line.startswith('+'):
                row = [int(x.strip()) for x in line.split('|')[1:-1]]
                matrix.append(row)
    return matrix


def spiral_traverse(matrix: List[List[int]]) -> List[int]:
    """
    Осуществляет обход матрицы по спирали против часовой стрелки.

    Args:
        matrix (List[List[int]]): Квадратная матрица NxN, состоящая из целых чисел.

    Returns:
        List[int]: Список значений, полученный путем обхода матрицы по спирали.
    """
    if not matrix or not matrix[0]:
        return []

    result = []
    top, bottom = 0, len(matrix)-1
    left, right = 0, len(matrix[0])-1

    while top <= bottom and left <= right:
        # Обход сверху-вниз по левому краю
        for i in range(top, bottom+1):
            result.append(matrix[i][left])
        left += 1

        # Обход слева-направо по нижнему ряду
        for j in range(left, right+1):
            result.append(matrix[bottom][j])
        bottom -= 1

        # Обход снизу-вверх по правому краю
        if top <= bottom:
            for i in range(bottom, top-1, -1):
                result.append(matrix[i][right])
            right -= 1

        # Обход справа-налево по верхнему ряду
        if left <= right:
            for j in range(right, left-1, -1):
                result.append(matrix[top][j])
            top += 1

    return result


def get_matrix(filename: str) -> List[int]:
    """
    Получает матрицу из файла и возвращает результат обхода по спирали.

    Args:
        filename (str): Имя файла, содержащего матрицу.

    Returns:
        List[int]: Список чисел, представляющих результат обхода матрицы по спирали.
    """
    try:
        matrix = read_matrix_from_file(filename)
        
        # Проверка, является ли матрица квадратной
        first_row_len = len(matrix[0])
        for row in matrix:
            if len(row) != first_row_len:
                raise ValueError("Матрица должна быть квадратной.")
        
        return spiral_traverse(matrix)
    except FileNotFoundError:
        print(f"Ошибка: файл '{filename}' не найден.")
        return []
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return []

# Пример использования
if __name__ == "__main__":
    result = get_matrix('matrix.txt')
    print(result)
