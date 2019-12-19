#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
pyhack.py : main file.
Nicolas VINCENT / Alan Dione
Projet pyhack (voir pyhack.pdf)

On stocke l'état d'une case dans un array numpy 2D

Room représente une pièce sur la carte

On place les pièces. On crée ensuite un labyrinthe entre les pièces.
Finalement, on relie le tout et on supprime les couloirs inutiles

"""


import argparse
import functools
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

from pyhack.carte import Map
from pyhack.const import (
    CONNECTOR,
    CORRIDOR,
    EMPTY,
    ENTRANCE,
    GOAL,
    MAIN_LOGGER,
    PLAYER,
    ROOM,
    VISITED,
)
from pyhack.utils import setup_custom_logger

# Vérification de la version de l'installation
try:
    assert sys.version_info >= (3, 6)
except AssertionError:
    raise SystemExit(
        "Ce jeu ne supporte pas Python {}.".format(platform.python_version()),
        "Installer une version supérieure à 3.6 pour le faire tourner.",
        "(we love fstrings ;) )",
    )


__version__ = "1.0.0"
__author__ = "VINCENT Nicolas" + "Alan Dione"
__licence__ = "GPLv3"


HERE = os.path.abspath(os.path.dirname(__file__))

# pylint: disable=logging-format-interpolation
# pylint: disable=logging-fstring-interpolation
LOGGER = setup_custom_logger("", HERE)  # pylint: disable=no-member
LOGGER.info(f"Setting up {MAIN_LOGGER} logger in {Path(__file__).stem}.py")


# Différents mouvements possibles
# touches directionnelles: ^[[A^[[B^[[D^[[C
AVANCER = "z"
RECULER = "s"
GAUCHE = "q"
DROITE = "d"


# Gestion de l'affichage
AFFICHAGE_DEBUG = {
    EMPTY: "#",
    VISITED: "v",
    PLAYER: "@",
    ROOM: "r",
    CORRIDOR: "c",
    GOAL: "!",
    CONNECTOR: "#",
    ENTRANCE: "e",
}

AFFICHAGE = {
    EMPTY: "#",
    VISITED: ".",
    PLAYER: "@",
    ROOM: ".",
    CORRIDOR: ".",
    GOAL: "!",
    CONNECTOR: "#",
    ENTRANCE: ".",
}

DEFAULT_SIZE = (60, 60)


class OutOfWalkableError(Exception):
    """Raised when you try to move in a wall."""


def draw_board(board, affichage, cases_visibles):
    """Affiche le dongeon sur le terminal.

    # TODO: sauvegarder plusieurs plateaux de debug
    Pour le mode debug: AFFICHAGE_DEBUG et carte.cases

    Parameters:
        self.board (np.ndarray): tableau 2D représentant le plateau
        affichage (dict): dictionnaire contenant les caractères affichés

    """
    for colonne in range(board.shape[1]):
        for ligne in range(board.shape[0]):
            tile = board[ligne][colonne]
            if (ligne, colonne) in cases_visibles:
                print(affichage[tile], end=" ")
            else:
                print(" ", end=" ")
        print()


def clear():
    """Modifie l'affichage."""
    LOGGER.debug("Clear terminal")
    subprocess.Popen("cls" if platform.system() == "Windows" else "clear", shell=True)
    time.sleep(0.01)


def while_true(func):
    """Décore la fonction d'une boucle while True pour les inputs.

    Erreurs personnalisées.

    Requires:
        OutOfWalkableError (Exception): //

    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        while True:
            try:
                res = func(*args, **kwargs)
                if res == "verif":
                    continue
                break
            except ValueError:
                LOGGER.warning("Entrer une direction valide.")
            except OutOfWalkableError:
                LOGGER.warning("Un mur vous empêche d'avancer.")
        return res

    return wrapper


@while_true
def get_input_direction(carte):
    """Prend en entrée la direction.

    Parameters:
        carte (Map): carte pour laquelle est généré le plateau de jeu
        self.board (np.ndarray): tableau 2D représentant le plateau

    Returns:
        direction (str): //
        movements (dict): coordonnées des mouvements possibles

    """
    LOGGER.debug("Getting direction.")
    direction = input(
        f"Donner la direction ({AVANCER}, {RECULER}, {GAUCHE}, {DROITE}): "
    )
    movements = get_movements(carte.localisation_player)
    # Exit case
    if direction in ["quit", "exit"]:
        return direction, movements
    # Checks
    LOGGER.debug("Checking direction.")
    if direction not in [AVANCER, RECULER, GAUCHE, DROITE]:
        raise ValueError()
    LOGGER.debug("Checking if movement is allowed.")
    if carte.bad_movement(direction, movements):
        raise OutOfWalkableError()

    return direction, movements


def get_movements(current_localisation):
    """Renvoie un dictionnaire des mouvements possibles.

    Parameters:
        current_localisation (tuple): //

    """
    ligne, colonne = current_localisation
    return {
        AVANCER: (ligne, colonne - 1),
        RECULER: (ligne, colonne + 1),
        GAUCHE: (ligne - 1, colonne),
        DROITE: (ligne + 1, colonne),
    }


def get_terminal_size():
    """Renvoie la taille du terminal.

    Returns:
        rows, columns (tuple): //

    """
    LOGGER.debug("Getting terminal size.")
    return (
        DEFAULT_SIZE
        if platform.system() == "Windows"
        else map(int, subprocess.check_output(["stty", "size"]).decode().split())
    )


def create_parser():
    """Création du parser et de tous ses arguments.

    Returns:
        args (class instance): Argument entrés en ligne de commande.
        parser (class instance): Parser de la ligne de commande.

    Raises:
        parser.error: Erreurs des inputs sur le cmd.

    """
    LOGGER.debug("Création du parser.")

    # Initialisation du parser
    parser = argparse.ArgumentParser(
        prog="pyhack.py",
        description="Jeu pyhack",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument("-d", "--debug", action="store_true", help="enable debug mode")
    parser.add_argument(
        "-m", "--show-all-map", action="store_true", help="disable field of view"
    )

    args = parser.parse_args()
    return args, parser


def main():
    """main function."""
    args, _ = create_parser()
    height, width = get_terminal_size()
    # on laisse un espace entre les colonnes mais pas entre les lignes
    carte = Map(height - 1, width // 2)
    carte.gen_board()
    # check debug mode and field of view
    affichage = AFFICHAGE
    if args.show_all_map:
        LOGGER.debug("Field of view turned of.")
    if args.debug:
        LOGGER.debug("Debug mode turned on.")
        affichage = AFFICHAGE_DEBUG
    # main loop
    while carte.localisation_player != carte.goal:
        # Affichage
        draw_board(
            carte.board,
            affichage,
            carte.cases if args.show_all_map else carte.visibles_cases,
        )
        direction, movements = get_input_direction(carte)
        if direction in ["quit", "exit"]:
            break
        carte.move_entity(PLAYER, movements[direction], carte.localisation_player)
        carte.localisation_player = movements[direction]
        carte.discovered.add(carte.localisation_player)
        clear()
    print("\nYou made it!")


if __name__ == "__main__":
    main()
    # carte = Map(200, 200)
    # carte.gen_board()
