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

def generateIndependentSets(matrix, numMethod, methodList):
    #(rows, cols) = matrix.nonzero()
    independent_vertex_set_set = set()

    for k in range(10):
#        print "iteration"
        independent_vertex_set_len = len(independent_vertex_set_set)
        methodIdxs = list(range(numMethod))
        random.shuffle(methodIdxs, random.random)
        independent_vertex_temp_set = set()
        independent_vertex_set = set(range(numMethod))

        while len(independent_vertex_set) > 0:
            next_independent_vertex_set = set()
            next_methodIdxs = []

            for i in methodIdxs:
                for j in methodIdxs:
                    if i == j:
                        continue
                    method1 = methodList[i]
                    method2 = methodList[j]
                    hasMethodLink = matrix[i, j] > 0
                    if (i in independent_vertex_set) and (j in independent_vertex_set) and (hasMethodLink or hasFieldLink(method1, method2)):
                        independent_vertex_set.remove(j)
                        next_independent_vertex_set.add(j)
                        next_methodIdxs.append(j)
            methodIdxs = next_methodIdxs
            random.shuffle(methodIdxs)
            fivs = frozenset(independent_vertex_set)

            rm = set()
            for vs in independent_vertex_temp_set:
                if vs < fivs:
                    rm.add(vs)
                if fivs < vs:
                    rm.add(fivs)

            independent_vertex_temp_set.add(fivs)

            for vs in rm:
                independent_vertex_temp_set.remove(vs)
            #print "indendent set: %s" % str(independent_vertex_set)
#            print "independent temp set: %s %d" % (str(independent_vertex_temp_set), len(independent_vertex_temp_set))
            independent_vertex_set = next_independent_vertex_set
        independent_vertex_set_set = independent_vertex_set_set | independent_vertex_temp_set
    

#    print "independent set: %s %d" % (str(independent_vertex_set_set), len(independent_vertex_set_set))
    return independent_vertex_set_set

