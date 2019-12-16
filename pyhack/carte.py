#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
carte.py : Fichier contenant la classe Map.
"""


import logging
import subprocess
from collections import namedtuple
from pathlib import Path
from random import choice, randrange

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
    WALKABLE,
)
from pyhack.structures import Room
from pyhack.utils import add_tuple, get_cases, get_direction, positions_voisines

try:
    import numpy as np
except ImportError:
    subprocess.run(
        ["python3", "-m", "pip", "install", "-r", "../requirements.txt"], check=True
    )
    raise SystemExit()


DIRECTIONS = set([(1, 0), (0, 1), (-1, 0), (0, -1)])


class Map:
    """Carte du jeu.

    Attributes:
         (type): description

    """

    # pylint: disable=too-many-instance-attributes

    __slots__ = (
        "logger",
        "width",
        "height",
        "board",
        "cases",
        "inner_cases",
        "start",
        "goal",
        "localisation_player",
        "discovered",
        "rooms_positions",
        "mazes_positions",
        "all_voisins",
        "connecteurs",
        "connected",
    )

    MAX_ROOMS = 100
    MIN_ROOM_SIZE = 3
    MAX_ROOM_SIZE = 7
    VISIBILITY = 5
    LOGGER_NAME = MAIN_LOGGER + "." + Path(__file__).stem

    def __init__(self, height, width):
        """Initialise la carte.

        Parameters:
             width (int): largeur de la Carte
             height (int): hauteur de la Carte

        """
        self.logger = logging.getLogger(Map.LOGGER_NAME + "." + Map.__name__)
        self.logger.info("Création d'une instance de Map.")

        self.width = width
        self.height = height

        # tableau
        self.board = np.zeros(shape=(self.width, self.height))

        # TODO: faire une fonction pour le set des cases
        self.cases = get_cases(0, self.width, 0, self.height)
        # ensemble des possibilités de génération (on exclut la limite du plateau)
        self.inner_cases = get_cases(1, self.width - 1, 1, self.height - 1)

        self.set_regions_parameters()

        self.start = None
        self.goal = None

        # variables modifiables
        self.localisation_player = self.start
        self.discovered = set()

    def set_regions_parameters(self):
        """Paramètres par défauts des pièces de la carte."""
        self.logger.info("Attribution des paramètres des pièces.")

        # [room1, room2, ...] où room1 est une instance de Room
        # TODO: remplacer rooms_positions par rooms
        self.rooms_positions = []
        self.mazes_positions = []

        # cProfile: il est moins couteux de chercher les voisins de positions
        # dans un dictionnaires des voisins que de rappeler la fonction donnant
        # les voisins.
        self.all_voisins = self.get_voisins()

        # va contenir des namedtuple(position, liste des régions voisines) non
        # hashable donc pas de set
        self.connecteurs = []
        # contient toutes les cases que l'on peut parcourir
        self.connected = set()

    def set_game_parameters(self):
        """Paramètres par défauts du jeu.

        Les positions de départ et d'arrivée ne doivent pas se trouver dans
        la même pièce.

        """
        self.logger.info("Attribution des paramètres du jeu.")
        flat_rooms_positions = [
            position
            for room_positions in self.rooms_positions[1:]
            for position in room_positions
        ]
        self.start = choice(list(self.rooms_positions[0]))
        self.goal = choice(flat_rooms_positions)
        self.logger.info(f"Start: {self.start}, Goal: {self.goal}")

        # Initialisation de la position du joueur
        self.localisation_player = self.start

    def gen_board(self):
        """Génère le plateau de jeu 2D.

        On représente une pièce par 1, un joueur par 2, rien par 0

        Parameters:
            carte (Map): carte pour laquelle est généré le plateau de jeu

        Returns:
            self.board (np.ndarray): tableau 2D représentant le plateau

        """
        self.logger.info("Génération du plateau de jeu.")
        # get rooms
        rooms = self.get_rooms()
        # set rooms
        self.place_rooms(rooms)
        # create maze corridors
        self.fill_maze()

        # get_connecteurs
        self.set_connecteurs()
        self.connect_regions()
        self.remove_dead_ends()

        self.set_game_parameters()
        # set initial player position in a room
        self.set_tile(self.start, PLAYER)
        self.set_tile(self.goal, GOAL)

    def place_rooms(self, rooms):
        """Place les pièces générées sur la carte.

        Parameters:
            carte (Map): carte pour laquelle est généré le plateau de jeu
            self.board (np.ndarray): tableau 2D représentant le plateau

        Returns:
            self.board (np.ndarray): tableau 2D contenant les pièces générées

        """
        self.logger.info(f"Positionnement des pièces sur la carte")
        for room in rooms:
            for position in room.cases:
                self.board[position] = ROOM
            self.rooms_positions.append(room.cases)

    def get_rooms(self):
        """Génère les pièces sur la carte.

        # TODO: implémenter BSP pour une meilleur répartition

        Returns:
            rooms (list): liste contenant les pièces générées

        """
        self.logger.info("Génération des pièces.")
        rooms = []

        for _ in range(self.MAX_ROOMS):
            width = randrange(self.MIN_ROOM_SIZE, self.MAX_ROOM_SIZE)
            height = randrange(self.MIN_ROOM_SIZE, self.MAX_ROOM_SIZE)
            # on veut une délimitation autour des pièces
            abscisse = randrange(1, self.width - width - 1)
            ordonnee = randrange(1, self.height - height - 1)

            new_room = Room(abscisse, ordonnee, width, height)

            # on ajoute la pièce si elle n'en chevauche aucune autre
            failed = any(new_room.intersect(other_room) for other_room in rooms)

            if not failed:
                rooms.append(new_room)

        return rooms

    def get_voisins(self):
        """Renvoie les voisins de toutes les cases de la carte.

        Parameters:
            self.inner_cases (set): cases du plateau sans la limite extérieure

        Returns:
            (dict): dictionnaires position::voisins

        """
        return {
            position: positions_voisines(position, DIRECTIONS).intersection(self.cases)
            for position in self.inner_cases
        }

    def fill_maze(self):
        """Rempli la carte avec un labyrinthe serpentant entre les pièces.

        Parameters:
            carte (Map): carte pour laquelle est généré le plateau de jeu
            self.board (np.ndarray): tableau 2D représentant le plateau

        Returns:
            self.board (np.ndarray): tableau 2D contenant le labyrinthe des couloirs

        """
        self.logger.info("Remplissage de la carte par des labyrinthes.")
        for position in self.inner_cases:
            voisins = self.all_voisins[position]
            # autorisé si on peut construire un labyrinthe à partir de position
            allowed = self.check_empty_voisins(
                voisins
            ) and self.check_more_than_one_case(position)

            if allowed:
                self.gen_maze(position)

    def get_possibles_directions(self, position):
        """Renvoie une liste des directions possibles.

        Parameters:
            position (tuple): //

        Returns:
            (list): possibles directions

        """
        return [
            direction
            for direction in DIRECTIONS
            if self.couloir_possible(position, direction)
        ]

    def check_empty_voisins(self, voisins):
        """Vérifie que les positions du set voisins sont vides.

        Parameters:
            voisins (set): //

        Returns:
            (boolean)

        """
        return all(self.board[voisin] == EMPTY for voisin in voisins)

    def check_more_than_one_case(self, position):
        """Vérifie que le labyrinthe construit à partir de position contient plus d'une case.

        Parameters:
            position (tuple): //

        Returns:
            (boolean)

        """
        return bool(self.get_possibles_directions(position))

    def couloir_possible(self, position, direction):
        """Renvoie si l'on peut aller dans cette direction.

         - on ne doit pas toucher de pièce ou d'autre couloir

        Parameters:
            position (tuple): //
            direction (tuple): //

        Returns:
            (boolean)

        """
        next_case = add_tuple(position, direction)
        voisins = positions_voisines(next_case, DIRECTIONS)
        voisins.remove(position)
        voisins.add(next_case)

        correct_voisins = voisins.intersection(self.inner_cases)
        if not correct_voisins:
            return False
        return self.check_empty_voisins(correct_voisins)

    def gen_maze(self, position):
        """Génère un labyrinthe à partir de la position fournie.

        On crè une liste des cases du labyrinthe ne contenant que position initialement.
        On construit le labyrinthe à partir de la dernière case de ce tableau.
        Lorsque l'on ne peut plus continuer, supprime le dernier élément et on itère.

        Parameters:
            position (tuple): //

        """
        self.logger.debug("Génération d'un labyrinthe.")
        maze_cases = [position]
        maze_positions = set()
        maze_positions.add(position)

        last_direction = None
        self.board[position] = CORRIDOR

        while maze_cases:
            case = maze_cases[-1]
            possible_direction = self.get_possibles_directions(case)
            if possible_direction:
                direction = get_direction(possible_direction, last_direction)
                new_case = add_tuple(case, direction)
                self.board[new_case] = CORRIDOR
                maze_cases.append(new_case)
                maze_positions.add(new_case)
                last_direction = direction
            else:
                del maze_cases[-1]
                last_direction = None

        self.mazes_positions.append(maze_positions)
        self.logger.debug(f"Labyrinthe de taille {len(maze_positions)} généré.")

    def set_connecteurs(self):
        """Trouve toutes les cases pouvant servir de connecteurs.

        (Optionnels)
        # TODO: on ne veut pas plus de max_entrance entrée pour chaque pièce,
        on choisit donc seulement max_entrances connecteurs par pièce
        # TODO: min_entrance de 2 ?

        Parameters:
            self.inner_cases (set): cases du plateau autorisées

        Returns:
            self.connecteurs (list): liste des connecteurs possibles

        """
        self.logger.debug(f"Getting possible connectors.")
        Connecteur = namedtuple("Connecteur", "position regions_voisines")
        # possibles_connecteurs = self.mazes_positions + list(
        #     map(lambda room: room.connecteurs, self.rooms_positions)
        # )
        for position in self.inner_cases:
            regions_voisines = self.check_connecteur(position)
            # si plus de deux régions touchent position
            if len(regions_voisines) > 1:
                connecteur = Connecteur(position, regions_voisines)
                self.connecteurs.append(connecteur)
                self.board[position] = CONNECTOR

    def check_connecteur(self, position):
        """Renvoie les régions autour de la case position.

        (si la case position peut servir de connecteur)
        La case doit être EMPTY et adjacente d'au moins deux cases
        appartenant à deux régions différentes.

        TODO: OPTIMISER

        Parameters:
            position (tuple): //

        Returns:
            regions_differentes_voisines (list): régions voisines du connecteur

        """
        if position is EMPTY:
            return None
        # non rajouté en attribut car modifié par la suite
        regions = self.rooms_positions + self.mazes_positions
        voisins = self.all_voisins[position]
        regions_differentes_voisines = []
        for voisin in voisins:
            for region in regions:
                if voisin in region:
                    regions.remove(region)
                    regions_differentes_voisines.append(region)
                    break
        return regions_differentes_voisines

    def connect_regions(self):
        """Regroupement des différentes régions avec un connecteur.

        Parameters:
            self.rooms_positions, self.mazes_positions (list): régions du plateau

        Returns:
            self.connected (set): set des cases connectées

        """
        self.logger.info("Connection des régions.")
        regions = self.rooms_positions + self.mazes_positions

        # ISSUE: Room connected to itself apart from the game
        while regions:
            connecteur = choice(self.connecteurs)
            self.board[connecteur.position] = ENTRANCE
            # décrémente les régions qui restent à traiter
            # les sets plus rapide qu'une compréhension de liste
            regions = list(
                set(map(frozenset, regions))
                - set(map(frozenset, connecteur.regions_voisines))
            )

            voisins = self.all_voisins[connecteur.position]
            voisins.add(connecteur.position)

            self.connecteurs = list(
                filter(lambda c: c.position not in voisins, self.connecteurs)
            )
            # add connected regions to connected
            self.connected.add(connecteur.position)
            for region in connecteur.regions_voisines:
                self.connected.update(region)

        self.logger.debug("Régions connectées.")

    def remove_dead_ends(self):
        """Supprime les portions de labyrinthe inutiles.

        TODO: OPTIMISER

        """
        self.logger.debug("Suppression des portions de couloir inutiles.")
        done = False
        while not done:
            done = True
            for position in self.connected:
                # on ne traite pas les cases modifiées en mur
                if self.board[position] == EMPTY:
                    continue
                # s'il n'y a qu'une sortie, c'est une case inutile
                exits_count = 0
                voisins = self.all_voisins[position]
                for voisin in voisins:
                    if self.board[voisin] in WALKABLE:
                        exits_count += 1
                if exits_count != 1:
                    continue

                done = False
                self.board[position] = EMPTY

    def set_tile(self, position, tile_type):
        """Assign tile_type sur la position du plateau.

        Parameters:
            position (tuple): position du plateau
            self.board (np.ndarray): tableau 2D représentant le plateau
            tile_type (int): type de case

        Returns:
            self.board (np.ndarray): tableau 2D avec tile_type sur position

        """
        ligne, colonne = position
        self.board[ligne][colonne] = tile_type

    def move_entity(self, entity, position, previous_position):
        """Déplace le joueur sur la position.

        Parameters:
            entity (string): entité à déplacer
            position (tuple): //
            previous_position (tuple): //

        """
        self.logger.debug(f"Déplacement de l'entité {entity} sur la case {position}")
        self.set_tile(position, entity)
        self.set_tile(previous_position, VISITED)

    def bad_movement(self, direction, movements):
        """Vérification de la possibilité du mouvement sur le plateau.

        Parameters:
            direction (str): //
            movements (dict): movements possibles

        Returns:
            (bool): True si le mouvement n'emmène pas sur une pièce ou un couloir

        """
        ligne, colonne = movements[direction]
        return not self.board[ligne][colonne] in WALKABLE | {VISITED}

    @property
    def visibles_cases(self):
        """Renvoie les cases visibles.

        Parameters:
            self.board (np.ndarray): //
            self.localisation_player (tuple): //
            self.all_voisins (dict): //

        Returns:
            visibles (set): cases visibles depuis la position du joueur

        """
        voisins = self.all_voisins[self.localisation_player]
        # Initialisation des cases visibles
        visibles = set()
        visibles.update(voisins)
        # while voisins:
        # ajoute les voisins des voisins dans les cases visibles
        for _ in range(Map.VISIBILITY):
            new_voisins = voisins.copy()
            for case in voisins:
                if self.board[case] not in [EMPTY, CONNECTOR]:
                    new_voisins.update(self.all_voisins[case])
                visibles.add(case)
            new_voisins.symmetric_difference(voisins)
            voisins = new_voisins

        return visibles
