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

    i = 0;
    for mrClass in model.getClasses():
        for mrMethod in mrClass.getMethods():
            entities.append(mrMethod)
            entitiesIdxMap[mrMethod] = i
        for mrField in mrClass.getFields():
            entities.append(mrField)
            entitiesIdxMap[mrField] = i
        i = i + 1

    g = Graph(len(entities))
    for i in range(len(entities)):
        g.vs[i]["MREntity"] = entities[i]
        for outgoingDep in entities[i].getOutgoingDeps():
            g.add_edges([(i, entitiesIdxMap[outgoingDep])])

#   reset idx map
    entitiesIdxMap = {}

    print >> sys.stderr, "Finding independent vertex sets...",
    independent_vertex_set = g.maximal_independent_vertex_sets()
    print >> sys.stderr, "done"

    return independent_vertex_set
