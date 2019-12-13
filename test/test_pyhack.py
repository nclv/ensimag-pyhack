#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
Fichier de tests.

cd pyhack/
pipenv run pytest (-s for printing all)

"""

# ne pas importer directement de pyhack, tester seulement les sous-modules
# car il y a dans pyhack import log qui doit être changé en from pyhack import log

# from pyhack import pyhack
# carte = pyhack.Map(200, 200)


def inc(x):
    return x + 1


def test_answer():
    assert inc(3) == 4
