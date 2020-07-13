import pytest
from data_structures.propagate import PropagateVector, PropagateMatrix  # , PropagateMatrixSimple


def main():
    # test_simple_matrix()
    test_efficient_matrix()
    test_vector()


# def test_simple_matrix():
#     matrix = PropagateMatrixSimple((5, 5))
#     run_test_matrix(matrix)


def check_equal(matrix, expected):
    for i in range(len(expected)):
        for j in range(len(expected[0])):
            print("Checking i={}, j={}".format(i, j))
            assert matrix[j, i] == expected[i][j], "Expected M[{}, {}]={} but found {}".format(i, j, expected[i][j], matrix[j, i])


def test_efficient_matrix():
    matrix = PropagateMatrix((5, 5))
    run_test_matrix(matrix)


def test_set_get_frame():
    matrix = PropagateMatrix((5, 3))
    a = [0, 1, 2]
    b = [2, 4, 6]
    c = [1, 2, 3]

    matrix.set_frame(0, a)
    matrix.set_frame(1, b)
    matrix.set_frame(2, c)

    assert matrix.get_frame(0) == a, "Expected {}, got {}".format(a, matrix.get_frame(0))
    assert matrix.get_frame(1) == b, "Expected {}, got {}".format(b, matrix.get_frame(1))
    assert matrix.get_frame(2) == c, "Expected {}, got {}".format(c, matrix.get_frame(2))


def test_set_frame():
    matrix = PropagateMatrix((3, 5))
    a = [0, 1, 2, 3, 4]
    b = [7, 6, 5, 4, 3]
    c = [-1, -2, -3, -4, -5]
    matrix.set_frame(0, a)
    matrix.set_frame(1, b)
    matrix.set_frame(2, c)
    print(matrix)

    expected = [
        [0, 7, -1],
        [1, 6, -2],
        [2, 5, -3],
        [3, 4, -4],
        [4, 3, -5],
    ]

    check_equal(matrix, expected)


def test_get_frame():
    matrix = PropagateMatrix((5, 5))


def run_test_matrix(matrix):
    matrix[2, 1] = "abc"
    matrix[3, 4] = "123"
    matrix[1, 3] = 123
    matrix[4, 3] = 456
    matrix[3, 3] = 987

    expected = [
        [None, None, None, None, None],
        [None, None, "abc", "abc", "abc"],
        [None, None, None, None, None],
        [None, 123, 123, 987, 456],
        [None, None, None, "123", "123"],
    ]

    check_equal(matrix, expected)


def test_vector():
    test = PropagateVector(10)
    for i in range(10):
        print(test[i], end=" ")

    test[5] = "abc"
    test[2] = "123"
    test[7] = "duck"

    print(test)
    expected = [None, None, "123", "123", "123", "abc", "abc", "duck", "duck", "duck"]

    for i in range(10):
        assert test[i] == expected[i], "Expected test[{}] = {} but found {}".format(i, expected[i], test[i])


if __name__ == "__main__":
    main()
