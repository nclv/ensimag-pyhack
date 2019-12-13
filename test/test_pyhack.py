#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
Fichier de tests.

cd pyhack/
pipenv run pytest (-s for printing all)

"""

from pyhack import pyhack

print("La version du programme est", pyhack.__version__)


carte = pyhack.Map(200, 200)
# carte.gen_board()
