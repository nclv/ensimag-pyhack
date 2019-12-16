#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
utils.py : fichier contenant des fonctions utilitaires
"""


import logging
import os
from itertools import product
from operator import add
from random import choice, randrange


def add_tuple(tuple1, tuple2):
    """Ajoute les éléments de deux tuples.

    Parameters:
        tuple1/tuple2 (tuple): //

    Returns:
        (tuple): somme de tuple1 et de tuple2

    """
    return tuple(map(add, tuple1, tuple2))


def get_cases(absc_bottom_left, absc_bottom_right, ordo_bottom_left, ordo_top_left):
    """Renvoie les cases dans la zone délimitées par les coordonnées.

    Returns:
        (set): //

    """
    return set(
        product(
            range(absc_bottom_left, absc_bottom_right),
            range(ordo_bottom_left, ordo_top_left),
        )
    )


def positions_voisines(position, directions):
    """Retourne les positions voisines de position (haut/bas/gauche/droite).

    Parameters:
        position (tuple): case dont on veut connaitre les voisins

    Returns:
        voisins (set): position et ses voisins

    """
    voisins = {add_tuple(position, direction) for direction in directions}
    return voisins


def get_direction(possible_direction, last_direction):
    """Renvoie la direction suivante du labyrinthe.

    Parameters:
        possible_direction (list): //
        last_direction (tuple): //

    Returns:
        direction (tuple): prochaine direction

    """
    # on privilégie les couloirs droits avec une certaine probabilité
    choose_last_direction = last_direction in possible_direction and (
        randrange(0, 100) > 70
    )
    return last_direction if choose_last_direction else choice(possible_direction)


def setup_custom_logger(name, here):
    """Création d'un logger.

    On veut logger dans le terminal (ERROR) et dans un fichier de log (DEBUG).

    Debug (logger.debug): Provide very detailed output. Used for diagnosing
    problems.
    Info (logger.info): Provides information on successful execution. Confirms if
    things are working as expected.
    Warning (logger.warn or logger.warning): Issue a warning regarding a problem
    that might occur in the future or a recoverable fault.
    Error (logger.error): Indicates a problem in the software as it is not
    executing as expected.
    Critical (logger.critical): Indicates a serious error that might stop the
    program from running.

    """
    # create file handler which logs even debug messages
    filehandler = logging.FileHandler(
        filename=f"{here}/game.log", mode="w", encoding="utf-8"
    )
    filehandler.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    consolehandler = logging.StreamHandler()
    consolehandler.setLevel(logging.WARNING)
    # create formatter and add it to the handlers
    logformat = "%(asctime)s - %(name)-40s %(levelname)-8s %(message)s"
    fileformatter = logging.Formatter(fmt=logformat, datefmt="%d-%b-%y %H:%M:%S")
    consoleformatter = logging.Formatter(fmt="%(levelname)-8s %(message)s")
    filehandler.setFormatter(fileformatter)
    consolehandler.setFormatter(consoleformatter)
    # create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    # add the handlers to the logger
    logger.addHandler(filehandler)
    logger.addHandler(consolehandler)

    return logger
