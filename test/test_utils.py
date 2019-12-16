#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
test_utils.py
"""


import pytest  # pylint: disable=import-error

from pyhack.utils import add_tuple, get_cases, get_direction, positions_voisines


@pytest.mark.parametrize(
    "tuple1, tuple2, expected", [((0, 1), (1, 2), (1, 3)), ((-1, 1), (1, -4), (0, -3))]
)
def test_add_tuple(tuple1, tuple2, expected):
    assert add_tuple(tuple1, tuple2) == expected


def test_get_cases():
    assert get_cases(0, 5, 0, 5) == {
        (1, 3),
        (3, 0),
        (0, 2),
        (2, 1),
        (0, 3),
        (4, 0),
        (1, 2),
        (3, 3),
        (4, 4),
        (2, 2),
        (0, 4),
        (4, 1),
        (1, 1),
        (3, 2),
        (0, 0),
        (1, 4),
        (2, 3),
        (4, 2),
        (1, 0),
        (0, 1),
        (3, 1),
        (2, 0),
        (4, 3),
        (3, 4),
        (2, 4),
    }


@pytest.mark.parametrize(
    "position, directions, expected",
    [
        (
            (5, 5),
            set([(1, 0), (0, 1), (-1, 0), (0, -1)]),
            set([(4, 5), (5, 4), (6, 5), (5, 6)]),
        )
    ],
)
def test_positions_voisines(position, directions, expected):
    assert positions_voisines(position, directions) == expected


def test_get_direction():
    assert get_direction([(1, 0), (0, 1), (-1, 0), (0, -1)], (-1, 0)) in [
        (1, 0),
        (0, 1),
        (-1, 0),
        (0, -1),
    ]
