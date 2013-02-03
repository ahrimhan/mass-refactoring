from MRModel import *
from MREntity import *
import sys
from MRMethod import *
from MRField import *
from MRClass import *
from numpy import *
from generateIndependentSets import *
import scipy.sparse as sp

class MREngine:
    linkMatrix = None
    membershipMatrix = None
    model = None
    classes = None
    classIdxMap = None
    entities = None
    entityIdxMap = None
    numMethod = 0
    numField = 0
    independent_set = None
    
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

        self.numMethod = numMethod
        self.numField = numField

        methods = []
        fields = []
        for mrClass in model.getClasses():
            for mrMethod in mrClass.getMethods():
                methods.append(mrMethod)
            for mrField in mrClass.getFields():
                fields.append(mrField)

        methods = sorted(methods, key=lambda e:e.getName())
        fields = sorted(fields, key=lambda e:e.getName())

        for mrMethod in methods:
            entities.append(mrMethod)
        for mrField in fields:
            entities.append(mrField)

        methods = None
        fields = None

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
                if i != entityIdxMap[incomingDep]:
                    linkMatrix[i, entityIdxMap[incomingDep]] = 1
                    linkMatrix[entityIdxMap[incomingDep], i] = 1
                    numDep = numDep + 1

        print >> sys.stderr, "Class: %d, Method: %d, Field: %d dep:%d" % (numClass, numMethod, numField, numDep)

        self.linkMatrix = sp.coo_matrix(linkMatrix)
        self.membershipMatrix = sp.coo_matrix(membershipMatrix)
        self.classes = classes
        self.classIdxMap = classIdxMap
        self.entities = entities
        self.entityIdxMap = entityIdxMap
        self.model = model

    def getInternalExternalLinkMatrix(self):
        internal_link_mask = self.membershipMatrix * self.membershipMatrix.T
        internal_link_matrix = self.linkMatrix.multiply(internal_link_mask)
        external_link_matrix = self.linkMatrix - internal_link_matrix
        return (internal_link_matrix, external_link_matrix)

    def invertedMembershipMatrix(self, M):
        new_matrix = ones((len(self.entities), len(self.classes)), dtype='int32')
        (rows, cols) = M.nonzero()
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

    def getIndependentSet(self):
        if self.independent_set == None:
            self.independent_set = generateIndependentSets(sp.coo_matrix(methodMatrix), self.numMethod)
        return self.independent_set

    def getIndexOfPostiveMoveMethodCandidates(self, D):
        PD = D[0:self.numMethod, :]
        PD = PD - absolute(PD)
        PD = PD / 2
        PD = PD.astype('int32')
        candidateList = []
        rows_unique = []
        cols_unique = []

        (rows, cols) = PD.nonzero()

        for i in range(len(rows)):
            candidateList.append((rows[i], cols[i], D[rows[i], cols[i]]))

        return candidateList

    def getReferencedAttributesCount(self, methodId1, methodId2, classId):
        linkMatrix = self.linkMatrix.tocsr()
        methodMatrix1 = linkMatrix[methodId1, :]
        methodMatrix2 = linkMatrix[methodId2, :]
        print "methodMatrix1:%d" % methodId1
        print methodMatrix1
        print "methodMatrix2:%d" % methodId2
        print methodMatrix2


    def getCohesion(self):
        linkMatrix = self.linkMatrix.todense()
        print "linkMatrix"
        print linkMatrix
        print "membershipMatrix[method:%d, field:%d]" % (self.numMethod, self.numField)
        print self.membershipMatrix.todense()
        tdmMatrix = self.membershipMatrix.tocsc()[0:self.numMethod, :]
        (numFunc, numClass) =  tdmMatrix.shape
        print tdmMatrix.shape
        for classId in range(numClass):
            (funcIdMatrix, _) = tdmMatrix.getcol(classId).nonzero()
            print funcIdMatrix
            for funcIdId1 in range(len(funcIdMatrix)):
                for funcIdId2 in range(len(funcIdMatrix)):
                    if funcIdId1 < funcIdId2:
                        self.getReferencedAttributesCount(funcIdMatrix[funcIdId1], funcIdMatrix[funcIdId2], classId)

        #classNum = tdmMatrix.row
        #for rowId in range(classNum):
        #    print tdmMatrix[rowId, :]


    def getEvalMatrix(self):
        methodMatrix = self.linkMatrix.todense()[0:self.numMethod, 0:self.numMethod]
        #print "Idependent set:" + str(independent_set)

        (internal_matrix, external_matrix) = self.getInternalExternalLinkMatrix()
        IP = internal_matrix * self.membershipMatrix
        EP = external_matrix * self.membershipMatrix
        IIP = self.invertedMembershipMatrix(IP)
        D = IIP - EP
        return D

    def __repr__(self):
        return self.getName()
