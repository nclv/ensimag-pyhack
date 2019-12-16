#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
tiles_const.py : constantes des cases.
"""

# Différentes valeurs d'une case du plateau
EMPTY = 0
VISITED = 1
PLAYER = 2
ROOM = 3
CORRIDOR = 4
GOAL = 5
CONNECTOR = 6
ENTRANCE = 7

WALKABLE = {ROOM, CORRIDOR, ENTRANCE, GOAL}

MAIN_LOGGER = "pyhack"
