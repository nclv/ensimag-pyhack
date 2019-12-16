#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
test_structures.py
"""


import os

from pyhack.structures import Room
from pyhack.utils import setup_custom_logger

HERE = os.path.abspath(os.path.dirname(__file__))

LOGGER = setup_custom_logger("", HERE)  # pylint: disable=no-member
LOGGER.info(f"Setting up test_structures logger in test/")


def test_room_intersect():
    room1 = Room(0, 0, 5, 5)
    room2 = Room(5, 5, 3, 3)
    assert room1.intersect(room2)


def test_nombre_de_cases():
    room = Room(0, 5, 5, 5)
    assert len(room.cases) == room.nombre_de_cases


def test_connecteurs():
    room = Room(0, 0, 3, 3)
    assert room.cases == {
        (3, 2),
        (0, 0),
        (1, 3),
        (3, 0),
        (0, 2),
        (2, 1),
        (2, 3),
        (1, 0),
        (0, 3),
        (0, 1),
        (1, 2),
        (3, 3),
        (3, 1),
        (2, 0),
        (2, 2),
        (1, 1),
    }

    assert room.connecteurs == {
        (3, 2),
        (0, 0),
        (1, 3),
        (3, 0),
        (0, 2),
        (2, 3),
        (1, 0),
        (0, 3),
        (0, 1),
        (3, 3),
        (3, 1),
        (2, 0),
    }
