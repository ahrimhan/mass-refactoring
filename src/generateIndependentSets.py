import sys
from MRModel import *
from MREntity import *
from MRMethod import *
from MRField import *
from MRClass import *
from numpy import *
import scipy as sp
import random

def hasFieldLink(method1, method2):
    fieldSet1 = set()
    fieldSet2 = set()
    for entity in method1.outgoingDeps:
        if not entity.isMethod():
            fieldSet1.add(entity)

    for entity in method2.outgoingDeps:
        if not entity.isMethod():
            fieldSet2.add(entity)
    
    ret = len(fieldSet1 & fieldSet2) > 0
    #print "%s %s %d" % (method1.getName(), method2.getName(), len(fieldSet1 & fieldSet2))
    return ret

def generateIndependentSets(matrix, numMethod):
    (rows, cols) = matrix.nonzero()
    independent_vertex_set_set = set()

    for k in range(100):
        independent_vertex_set_len = len(independent_vertex_set_set)
        rowidxs = list(range(len(rows)))
        random.shuffle(rowidxs, random.random)
        #independent_vertex_temp_set = set()
        independent_vertex_set = set(range(numMethod))

        while len(independent_vertex_set) > 0:
            next_independent_vertex_set = set()
            next_row_idx = []
            #print "before", 
            #print independent_vertex_set
            #print "rowidxs"
            #print rowidxs
            #print "rows"
            #print rows
            #print "cols"
            #print cols
            for i in rowidxs:
                if rows[i] in independent_vertex_set and cols[i] in independent_vertex_set:
                    independent_vertex_set.remove(cols[i])
                    next_independent_vertex_set.add(cols[i])
                    next_row_idx.append(i)
            #rowidxs = next_row_idx
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
            #print "after",
            #print independent_vertex_set

            independent_vertex_set = next_independent_vertex_set
        #independent_vertex_set_set = independent_vertex_set_set | independent_vertex_temp_set

    #for independent_set in independent_vertex_set_set:
    #    for v1 in independent_set:
    #        for v2 in independent_set:
    #            if matrix[v1, v2] != 0:
    #                print "v1: %d v2:%d" % (v1, v2)

    return independent_vertex_set_set
