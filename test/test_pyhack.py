#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
Fichier de tests.

cd pyhack/
pipenv run pytest (-s for printing all)

"""


# from pyhack import pyhack

# carte = pyhack.Map(200, 200)


def inc(x):
    return x + 1


def test_answer():
    assert inc(3) == 4
