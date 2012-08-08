from MRModel import *
from MREntity import *
import sys
from MRMethod import *
from MRField import *
from MRClass import *
from numpy import *
import scipy.sparse as sp

class MREngine:
    linkMatrix = None
    membershipMatrix = None
    model = None
    classes = None
    classIdxMap = None
    entities = None
    entityIdxMap = None
    
    def initialize(self, model):
        classes = []
        classIdxMap = {}
        entities = []
        entityIdxMap = {}

        numClass = 0
        numMethod = 0
        numField = 0
        numDep = 0

        sortedClasses = sorted(model.getClasses(), key=lambda c: c.getName())

        for mrClass in sortedClasses:
            classes.append(mrClass)
            classIdxMap[mrClass] = numClass
            numMethod = numMethod + len(mrClass.getMethods())
            numField = numField + len(mrClass.getFields())
            numClass = numClass + 1

        for mrClass in model.getClasses():
            for mrMethod in mrClass.getMethods():
                entities.append(mrMethod)
            for mrField in mrClass.getFields():
                entities.append(mrField)

        entities = sorted(entities, key=lambda e:e.getName())

        i = 0;
        for mrEntity in entities:
            entityIdxMap[mrEntity] = i
            i = i + 1

        membershipMatrix = zeros((numMethod + numField, numClass), dtype='int32')

        for i in range(len(classes)):
            mrClass = classes[i]
            for mrMethod in mrClass.getMethods():
                membershipMatrix[entityIdxMap[mrMethod], i] = 1
            for mrField in mrClass.getFields():
                membershipMatrix[entityIdxMap[mrField], i] = 1
        
        linkMatrix = zeros((numMethod + numField, numMethod+numField), dtype='int32')

        for i in range(len(entities)):
            for incomingDep in entities[i].getIncomingDeps():
                linkMatrix[i, entityIdxMap[incomingDep]] = 1
                linkMatrix[entityIdxMap[incomingDep], i] = 1
                numDep = numDep + 1

        print >> sys.stderr, "Class: %d, Method: %d, Field: %d dep:%d" % (numClass, numMethod, numField, numDep)

        print "classes"
        print classes

        print "entities"
        print entities

        print "Link Matrix"
        print linkMatrix

        print "Initial Membership Matrix"
        print membershipMatrix

        self.linkMatrix = sp.coo_matrix(linkMatrix)
        self.membershipMatrix = sp.coo_matrix(membershipMatrix)
        self.classes = classes
        self.classIdxMap = classIdxMap
        self.entities = entities
        self.entityIdxMap = entityIdxMap
        self.model = model

    def getInternalExternalLinkMatrix(self):
        print >> sys.stderr, "internal_link_mask"
        internal_link_mask = self.membershipMatrix * self.membershipMatrix.T
        print >> sys.stderr, "internal_link_matrix"
        internal_link_matrix = self.linkMatrix.multiply(internal_link_mask)
        print >> sys.stderr, "external_link_matrix"
        external_link_matrix = self.linkMatrix - internal_link_matrix
        return (internal_link_matrix, external_link_matrix)

    def invertedMembershipMatrix(self, M):
        new_matrix = ones((len(self.entities), len(self.classes)), dtype='int32')
        (rows, cols) = M.nonzero()
        print "rows count:" + str(len(rows))
        print "entities count:" + str(len(self.entities))
        l = 0
        for p in range(len(self.entities)):
            if p in rows:
                j = cols[l]
                l = l + 1
                new_matrix[p, j] = 0
            else:
                for k in range(len(self.classes)):
                    new_matrix[p, k] = 0
        for i in range(len(rows)):
            new_matrix[i] = new_matrix[i] * M[rows[i], cols[i]]

        return sp.coo_matrix(new_matrix)

    def getEvalMatrix(self):
        print >> sys.stderr, "getInternalExternalLinkMatrix"
        (internal_matrix, external_matrix) = self.getInternalExternalLinkMatrix()
        print >> sys.stderr, "internal_link_matrix"
        print >> sys.stderr, internal_matrix
        print >> sys.stderr, "external_link_matrix"
        print >> sys.stderr, external_matrix
        print >> sys.stderr, "dot IP"
        IP = internal_matrix * self.membershipMatrix
        print IP.todense()
        print >> sys.stderr, "dot EP"
        EP = external_matrix * self.membershipMatrix
        print >> sys.stderr, "inv IIP"
        IIP = self.invertedMembershipMatrix(IP)
        print IIP.todense()
        print >> sys.stderr, "IIP-EP"
        D = IIP - EP
        print >> sys.stderr, "done"
        return D.todense()
    def __repr__(self):
        return self.getName()
