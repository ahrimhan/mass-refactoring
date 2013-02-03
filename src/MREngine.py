from MRModel import *
from MREntity import *
import sys
from MRMethod import *
from MRField import *
from MRClass import *
from numpy import *
from generateIndependentSets import *
from multiprocessing import Pool
from multiprocessing import Lock
import scipy.sparse as sp

global singletonEngine
singletonEngine = None

def cohesionForClasses(classId):
    global singletonEngine
    return singletonEngine.getCohesionForClass(classId)

class MREngine:
    linkMatrix = None
    membershipMatrix = None
    fieldLinkMatrix = None
    model = None
    classes = None
    classIdxMap = None
    entities = None
    entityIdxMap = None
    numMethod = 0
    numField = 0
    independent_set = None
    fieldsSelectingMatrix = None 
    methodMembershipMatrix = None
    pool = None

    def initialize(self, model):
        global singletonEngine
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

        fsmRow = array(range(self.numMethod, self.numMethod + self.numField))
        fsmCol = array(range(self.numMethod, self.numMethod + self.numField))
        fsmData = array([1] * self.numField)
        self.fieldsSelectingMatrix = sp.coo_matrix((fsmData, (fsmRow, fsmCol)), shape = (self.numMethod + self.numField, self.numMethod + self.numField)).tocsc()

        print >> sys.stderr, "Class: %d, Method: %d, Field: %d dep:%d" % (numClass, numMethod, numField, numDep)

        self.linkMatrix = sp.coo_matrix(linkMatrix).tocsr()
        self.fieldLinkMatrix = self.linkMatrix * self.fieldsSelectingMatrix
        self.fieldLinkMatrix = self.fieldLinkMatrix.tocsr()
        self.membershipMatrix = sp.coo_matrix(membershipMatrix).tocsr()
        self.classes = classes
        self.classIdxMap = classIdxMap
        self.entities = entities
        self.entityIdxMap = entityIdxMap
        self.model = model
        singletonEngine = self

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


    def getCohesionForMethodPair(self, methodId1, methodId2, classId):
        #refMatrix1 = linkMatrix[methodId1, :] * self.fieldsSelectingMatrix
        #refMatrix2 = linkMatrix[methodId2, :] * self.fieldsSelectingMatrix
        refMatrix1 = self.fieldLinkMatrix[methodId1, :]
        refMatrix2 = self.fieldLinkMatrix[methodId2, :]
        refMatrix3 = self.membershipMatrix[:, classId]
        #print refMatrix1.nonzero()
        (_, attr1) = refMatrix1.nonzero()
        (_, attr2) = refMatrix2.nonzero()
        (attr3, _) = refMatrix3.nonzero()
        attrSet3 = set(attr3)
        attrSet1 = set(attr1) & attrSet3
        attrSet2 = set(attr2) & attrSet3

        unionSet = attrSet1 | attrSet2
        interSet = attrSet1 & attrSet2

        #print interSet

        if len(unionSet) == 0:
            return 0

        return float(len(interSet)) / float(len(unionSet))

    def getCohesionForClass(self, classId):
        classCohesion = float(0)
        (funcIdMatrix, _) = self.methodMembershipMatrix.getcol(classId).nonzero()
        #print funcIdMatrix
        pairCount = 0
        for funcIdId1 in range(len(funcIdMatrix) - 1):
            for funcIdId2 in range(funcIdId1 + 1, len(funcIdMatrix)):
                pairCount = pairCount+1
                classCohesion = classCohesion + self.getCohesionForMethodPair(funcIdMatrix[funcIdId1], funcIdMatrix[funcIdId2], classId)
        if pairCount != 0:
            classCohesion = classCohesion / float(pairCount)
        else:
            classCohesion = 0
        #print "PairCount:%d(%d)" % (pairCount, len(funcIdMatrix))
        return classCohesion

    def getCohesion(self):
        linkMatrix = self.linkMatrix.todense()
        #print "linkMatrix"
        #print linkMatrix
        print "membershipMatrix[method:%d, field:%d]" % (self.numMethod, self.numField)
        print self.membershipMatrix.todense()
        self.methodMembershipMatrix = self.membershipMatrix[0:self.numMethod, :]
        (numFunc, numClass) =  self.methodMembershipMatrix.shape
        cohesion = float(0)
        self.pool = Pool(processes=4)
        retPool = self.pool.map(cohesionForClasses, range(numClass))
        for i in retPool:
            cohesion = cohesion + i
        cohesion = cohesion / numClass
        return cohesion

    def getCoupling(self):
        linkMatrix = self.linkMatrix
        self.methodMembershipMatrix = self.membershipMatrix[0:self.numMethod, :]
        (numFunc, numClass) = self.methodMembershipMatrix.shape
        coupling = float(0)
        for i in range(numClass):
            (funcIdList, _) = self.methodMembershipMatrix.getcol(classId).nonzero()
            funcIdSet = set(funcIdList)
            for j in funcIdList:
                (targetFuncIdList, _) = self.linkMatrix.getcol(j).nonzero()
                targetFuncIdSet = set(targetFuncIdList)
                externalCoupledFuncSet = targetFuncIdSet - funcIdSet
                coupling = coupling + len(externalCoupledFuncSet)
        coupling = coupling / nunClass
        return coupling
                
    def getEvalMatrix(self):
        methodMatrix = self.linkMatrix.todense()[0:self.numMethod, 0:self.numMethod]
        #print "Idependent set:" + str(independent_set)

        (internal_matrix, external_matrix) = self.getInternalExternalLinkMatrix()
        IP = internal_matrix * self.membershipMatrix
        EP = external_matrix * self.membershipMatrix
        IIP = self.invertedMembershipMatrix(IP)
        D = IIP - EP
        return D

    def getIndexOfPostiveMoveMethodCandidates(self, D):
        PD = D[0:self.numMethod, :]
        PD = PD - absolute(PD)
        PD = PD / 2
        PD = PD.astype('int32')
        candidateDict = {}
        (rows, cols) = PD.nonzero()
        for i in range(len(rows)):
            if rows[i] in candidateDict:
                (_, _, d) = candidateDict[rows[i]]
                if d < D[rows[i], cols[i]]:
                    candidateDict[rows[i]] = (rows[i], cols[i], D[rows[i], cols[i]])
            else:
                candidateDict[rows[i]] = (rows[i], cols[i], D[rows[i], cols[i]])
        return candidateDict

    def getElectMoveMethodCandidateSet(self, D):
        candidateDict = self.getIndexOfPostiveMoveMethodCandidates(self, D)
        independentSetSet = self.getIndependentSets()
        maxScore = 0
        maxCandidateSet = None
        for independentSet in independentSetSet:
            asetScore = 0
            candidateSet = [] 
            for methodIdx in independentSet:
                (m, c, d) = candidateDict[methodIdx]
                if d > 0:
                    asetScore = asetScore + d
                    candidateSet.append((m, c, d))
            if asetScore > maxScore:
                maxScore = asetScore
                maxCandidateSet = candidateSet
        return maxCandidateSet

    def updateMembershipMatrix(self, moveMethodSet)
        for (m, c, d) in moveMethodSet:
            (_, oldContainingClassIdxList) = self.membershipMatrix.getrow(m).nonzero()
            for cc in oldContainingClassIdxList:
                self.membershipMatrix[m, cc] = 0
            self.membershipMatrix[m, c] = 1

    def __repr__(self):
        return self.getName()
