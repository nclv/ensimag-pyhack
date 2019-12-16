#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
structures.py : fichier contenant la classe Room
"""


import logging
from pathlib import Path

from pyhack.const import MAIN_LOGGER
from pyhack.utils import get_cases


class Room:
    """Classe représentant une pièce.

    Une pièce est représentée par deux points de la diagonale de la pièce.

    Attributes:
         absc_bottom_left (int): //
         ordo_bottom_left (int): //
         absc_bottom_right (int): //
         ordo_top_left (int): //
         logger_name (str): name of the main logger.

    """

    __slots__ = (
        "logger",
        "absc_bottom_left",
        "ordo_bottom_left",
        "absc_bottom_right",
        "ordo_top_left",
    )
    LOGGER_NAME = MAIN_LOGGER + "." + Path(__file__).stem

    def __init__(self, abscisse, ordonnee, width, height):
        """Constructeur de la classe Room.

        Parameters:
            abscisse, ordonnee, width, height (int): //

        """
        self.logger = logging.getLogger(Room.LOGGER_NAME + "." + Room.__name__)
        self.logger.debug("Création d'une instance de Room.")

        self.absc_bottom_left = abscisse
        self.ordo_bottom_left = ordonnee
        self.absc_bottom_right = abscisse + width
        self.ordo_top_left = ordonnee + height

        self.logger.debug(f"La pièce comporte {self.nombre_de_cases} cases.")

    def intersect(self, room2):
        """Renvoie si deux pièces se chevauchent ou sont à côté.

        If the rectangles do not intersect, then at least one of the right sides
        will be to the left of the left side of the other rectangle (i.e. it will
        be a separating axis), or vice versa, or one of the top sides will be
        below the bottom side of the other rectange, or vice versa.

        On agrandit le premier rectangle pour empêcher les pièces d'être côte à côte

        self.inner_cases.isdisjoint(room2.cases) ne prend pas en compte les pièces
        côte à côte

        Parameters:
            room2 (Room): deuxième pièce

        Returns:
            (bool): True si les pièces se chevauchent

        """
        return (
            self.absc_bottom_left - 1 <= room2.absc_bottom_right
            and self.absc_bottom_right + 1 >= room2.absc_bottom_left
            and self.ordo_bottom_left - 1 <= room2.ordo_top_left
            and self.ordo_top_left + 1 >= room2.ordo_bottom_left
        )

    @property
    def cases(self):
        """Retourne toutes les cases d'une pièce.

        Returns:
            (set): cases

        """
        return get_cases(
            self.absc_bottom_left,
            self.absc_bottom_right + 1,
            self.ordo_bottom_left,
            self.ordo_top_left + 1,
        )

    @property
    def nombre_de_cases(self):
        """Retourne le nombre de cases dans une pièces.

        Indépendant de self.get_cases

        Returns:
            (int): nombre de cases

        """
        return (self.absc_bottom_right - self.absc_bottom_left + 1) * (
            self.ordo_top_left - self.ordo_bottom_left + 1
        )

    @property
    def connecteurs(self):
        """Renvoie les cases de la limite extérieure de la pièce.

        Returns:
            (set): connecteurs possibles de la pièce.

        """
        return self.cases.difference(
            get_cases(
                self.absc_bottom_left + 1,
                self.absc_bottom_right,
                self.ordo_bottom_left + 1,
                self.ordo_top_left,
            )
        )

    # TODO: room.get_count_entrance ?
