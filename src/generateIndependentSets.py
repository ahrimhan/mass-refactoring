import sys
from MRModel import *
from MREntity import *
from MRMethod import *
from MRField import *
from MRClass import *
from igraph import *

def generateIndependentSets(model):
    entities = []
    entitiesIdxMap = {}

    numClass = 0
    numMethod = 0
    numField = 0
    numDep = 0
    for mrClass in model.getClasses():
        numClass = numClass + 1
        numMethod = numMethod + len(mrClass.getMethods())
        numField = numField + len(mrClass.getFields())


    i = 0;
    for mrClass in model.getClasses():
        for mrMethod in mrClass.getMethods():
            entities.append(mrMethod)
            entitiesIdxMap[mrMethod] = i
            i = i + 1

    g = Graph(n=len(entities), directed=False)
    for i in range(len(entities)):
        g.vs[i]["MREntity"] = entities[i]
        for incomingDep in entities[i].getIncomingDeps():
            g.add_edges([(entitiesIdxMap[incomingDep], i)])
            numDep = numDep + 1

    print >> sys.stderr, "Class: %d, Method: %d, Field: %d dep:%d" % (numClass, numMethod, numField, numDep)
#   reset idx map

    print >> sys.stderr, "Finding independent vertex sets...",
#    independent_vertex_set = g.independent_vertex_sets(1, 5)
    independent_vertex_set = g.maximal_independent_vertex_sets()
    independent_vertex_set = map(lambda x: map(lambda y: entities[y].getName(), x), independent_vertex_set)
    print >> sys.stderr, "done"

    return independent_vertex_set
