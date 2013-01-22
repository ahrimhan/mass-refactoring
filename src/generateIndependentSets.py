import sys
from MRModel import *
from MREntity import *
from MRMethod import *
from MRField import *
from MRClass import *
from numpy import *
import scipy as sp
import random

def generateIndependentSets(matrix, numMethod):
    (rows, cols) = matrix.nonzero()
    independent_vertex_set_set = set()

    for k in range(50):
        independent_vertex_set_len = len(independent_vertex_set_set)
        rowidxs = list(range(len(rows)))
        random.shuffle(rowidxs, random.random)
        independent_vertex_set = set(range(numMethod))

        while len(independent_vertex_set) > 0:
            next_independent_vertex_set = set()
            next_row_idx = []
            for i in rowidxs:
                if rows[i] in independent_vertex_set and cols[i] in independent_vertex_set:
                    independent_vertex_set.remove(cols[i])
                    next_independent_vertex_set.add(cols[i])
                    next_row_idx.append(i)
            rowidxs = next_row_idx
            random.shuffle(rowidxs)
            fivs = frozenset(independent_vertex_set)

            rm = set()
            for vs in independent_vertex_set_set:
                if vs < fivs:
                    rm.add(vs)
                if fivs < vs:
                    rm.add(fivs)

            independent_vertex_set_set.add(fivs)

            for vs in rm:
                independent_vertex_set_set.remove(vs)

            independent_vertex_set = next_independent_vertex_set

    return independent_vertex_set_set

