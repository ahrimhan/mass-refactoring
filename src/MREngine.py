from MRModel import *
import time
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

def cohesionForClasses(clazz):
    global singletonEngine
    return singletonEngine.getCohesionForClass(clazz)

def epcHelper(classes):
    global singletonEngine
    return singletonEngine.getEntityPlacementWithClassId(classes)

class MREngine:
    linkMatrix = None
    #callLinkMatrix = None
    membershipMatrix = None
    model = None
    classes = None
    classIdxMap = None
    entities = None
    entityIdxMap = None
    methodPairDistanceCache = {}
    numMethod = 0
    numField = 0
    independent_set = None
    #fieldsSelectingMatrix = None 
    methodMembershipMatrix = None
    pool = None
    entitySetCache = {}
    methods = None

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
        self.methods = methods
        fields = sorted(fields, key=lambda e:e.getName())

        for mrMethod in methods:
            entities.append(mrMethod)
        for mrField in fields:
            entities.append(mrField)


        i = 0
        for mrEntity in entities:
            mrEntity.setIndex(i)
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
        #callLinkMatrix = zeros((numMethod + numField, numMethod+numField), dtype='int32')

        for i in range(len(entities)):
            for incomingDep in entities[i].getIncomingDeps():
                if i != incomingDep.getIndex():
                    linkMatrix[i, incomingDep.getIndex()] = linkMatrix[i, incomingDep.getIndex()] + 1
                    linkMatrix[incomingDep.getIndex(), i] = linkMatrix[incomingDep.getIndex(), i] + 1
                    #linkMatrix[i, incomingDep.getIndex()] = 1
                    #linkMatrix[incomingDep.getIndex(), i] = 1
            #        callLinkMatrix[i, incomingDep.getIndex()] = 1
            #        callLinkMatrix[incomingDep.getIndex(), i] = 1
                    numDep = numDep + 1


        if False:
            for field in fields:
                methodDep = []
                for dep in field.getIncomingDeps():
                    if dep.isMethod():
                        methodDep.append(dep)
                i = 0
                while i < len(methodDep) - 1:
                    j = i + 1
                    while j < len(methodDep):
                        linkMatrix[methodDep[i].getIndex(), methodDep[j].getIndex()] = linkMatrix[methodDep[i].getIndex(), methodDep[j].getIndex()] + 3
                        linkMatrix[methodDep[j].getIndex(), methodDep[i].getIndex()] = linkMatrix[methodDep[j].getIndex(), methodDep[i].getIndex()] + 3
                        j = j + 1
                    i = i + 1



        methods = None
        fields = None

        fsmRow = array(range(self.numMethod, self.numMethod + self.numField))
        fsmCol = array(range(self.numMethod, self.numMethod + self.numField))
        fsmData = array([1] * self.numField)
        #self.fieldsSelectingMatrix = sp.coo_matrix((fsmData, (fsmRow, fsmCol)), shape = (self.numMethod + self.numField, self.numMethod + self.numField)).tocsc()

        print "Class: %d, Method: %d, Field: %d dep:%d" % (numClass, numMethod, numField, numDep)

        self.linkMatrix = sp.coo_matrix(linkMatrix).tocsr()
        #self.callLinkMatrix = sp.coo_matrix(callLinkMatrix).tocsr()
        #self.membershipMatrix = sp.coo_matrix(membershipMatrix).tocsr()
        self.membershipMatrix = sp.coo_matrix(membershipMatrix).tolil()
        self.classes = classes
        self.classIdxMap = classIdxMap
        self.entities = entities
        self.entityIdxMap = entityIdxMap
        self.model = model
        singletonEngine = self
        #print "Initial state"
        #print "Link"
        #print self.linkMatrix.todense()
        #print "Membership"
        #print self.membershipMatrix.todense()
        #print "Class status"
        #print self.model

    def getInternalExternalLinkMatrix(self):
        internal_link_mask = self.membershipMatrix * self.membershipMatrix.T
        internal_link_matrix = self.linkMatrix.multiply(internal_link_mask)
        #print "internal link"
        #print internal_link_matrix.todense()

        external_link_matrix = self.linkMatrix - internal_link_matrix
        #print "external link"
        #print external_link_matrix.todense()
        return (internal_link_matrix, external_link_matrix)

    def invertedMembershipMatrix(self, M):
        #print "before"
        #print M.todense()
        #invertingTime = time.time()

        #new_matrix = ones((len(self.entities), len(self.classes)), dtype='int32')
        #(rows, cols) = M.nonzero()
        #l = 0
        #for p in range(len(self.entities)):
        #    if p in rows:
        #        j = cols[l]
        #        l = l + 1
        #        new_matrix[p, j] = 0
        #    else:
        #        new_matrix[p, :] = new_matrix[p, :] * 0
        #
        #for i in range(len(rows)):
        #    new_matrix[rows[i], :] = new_matrix[rows[i], :] * M[rows[i], cols[i]]

        #print "inverting..."
        new_matrix = zeros((len(self.entities), len(self.classes)), dtype='int32')
        (rows, cols) = M.nonzero()
        for i in range(len(rows)):
            v = M[rows[i], cols[i]]
            new_matrix[rows[i], :] = new_matrix[rows[i], :] + v
            new_matrix[rows[i], cols[i]] = 0

        #print "after"
        #print new_matrix

        ret  = sp.coo_matrix(new_matrix)

        #print "inverting time:%f" % (time.time() - invertingTime)
        return ret

    def getIndependentSets(self):
        if self.independent_set == None:
            self.independent_set = generateIndependentSets(self.linkMatrix, self.numMethod)
        return self.independent_set


    def getCohesionForMethodPair(self, method1, method2, clazz):
        #fields = clazz.getFields()
        #attrSet3 = set(fields)
        attrSet1 = set()
        attrSet2 = set()
        ret = 0
        if (method1, method2) in self.methodPairDistanceCache:
            return self.methodPairDistanceCache[(method1, method2)]

        for deps in method1.outgoingDeps:
            if not deps.isMethod():
                attrSet1.add(deps)

        for deps in method2.outgoingDeps:
            if not deps.isMethod():
                attrSet2.add(deps)

        unionSet = attrSet1 | attrSet2
        unionLen = len(unionSet)
        interLen = len(attrSet1) + len(attrSet2) - unionLen

        #print interSet

        if unionLen == 0:
            ret = 0
        else:
            ret = float(interLen) / float(unionLen)
        self.methodPairDistanceCache[(method1, method2)] = ret
        self.methodPairDistanceCache[(method2, method1)] = ret
        return ret

    def getCohesionForClass(self, clazz):
        classCohesion = float(0)
        pairCount = 0

        methods = clazz.getMethods()
         
        if len(methods) == 0:
            return -1

        funcIdId1 = 0
        while funcIdId1 < (len(methods) - 1):
            funcIdId2 = funcIdId1 + 1
            while funcIdId2 < len(methods):
                pairCount = pairCount+1
                classCohesion = classCohesion + self.getCohesionForMethodPair(methods[funcIdId1], methods[funcIdId2], clazz)
                funcIdId2 = funcIdId2 + 1
            funcIdId1 = funcIdId1 + 1
        if pairCount != 0:
            classCohesion = classCohesion / float(pairCount)
        else:
            classCohesion = -1
        #print "class:" + clazz.getName() + ":" + str(classCohesion)
        return classCohesion

    def getCohesion(self):
        #self.pool = Pool(processes=4)
        cohesion = 0
        classCount = 0
        for clazz in self.classes:
            if clazz.isCohesionDirty():
                classCohesion = self.getCohesionForClass(clazz)
                clazz.setCohesion(classCohesion)
            else:
                classCohesion = clazz.getCohesion()

            if classCohesion >= 0:
                cohesion = cohesion + classCohesion
                classCount = classCount + 1
        norm_cohesion = cohesion / classCount
        return (norm_cohesion, cohesion, classCount)

    def getDistance(self, entity, innerClazzEntities):
        ret = None
        #if entity in self.entitySetCache:
        #    ret = self.entitySetCache[entity]
        #else:
        #    if entity.isMethod():
        #        ret = frozenset(entity.getOutgoingDeps())
        #    else:
        #        ret = frozenset(entity.getIncomingDeps())
        #    self.entitySetCache[entity] = ret

        if entity.isMethod():
            ret = frozenset(entity.getOutgoingDeps())
        else:
            ret = frozenset(entity.getIncomingDeps())
        self.entitySetCache[entity] = ret
        se = ret
        sc = innerClazzEntities
        unionlen = len(se | sc)
        interlen = len(se) + len(sc) - unionlen
        if unionlen == 0:
            distance = -1
        else:
            distance = 1 - (interlen / float(unionlen))
        return distance

    def getEntityPlacementForClass(self, innerClazzEntities):
        if innerClazzEntities == 0 :
            return 0
        innerDistanceSum = 0
        outerDistanceSum = 0
        innerClazzEntityNum = 0
        outerClazzEntityNum = 0
        for entity in self.entities:
            if entity in innerClazzEntities:
                innerClazzEntityDistance = self.getDistance(entity, innerClazzEntities - set([entity]))
                if innerClazzEntityDistance >= 0:
                    innerDistanceSum = innerDistanceSum + innerClazzEntityDistance
                    innerClazzEntityNum = innerClazzEntityNum + 1
            else:
                outerClazzEntityDistance = self.getDistance(entity, innerClazzEntities)
                if outerClazzEntityDistance >= 0:
                    outerDistanceSum = outerDistanceSum + outerClazzEntityDistance
                    outerClazzEntityNum = outerClazzEntityNum + 1

        if outerDistanceSum == 0:
            return -1

        if outerClazzEntityNum == 0:
            return -1

        if innerClazzEntityNum == 0:
            return -1

        epc = (float(innerDistanceSum) / innerClazzEntityNum) / (float(outerDistanceSum) / outerClazzEntityNum)
        return epc

    def getEntityPlacementWithClass(self, clazz):
        if not clazz.isEpsDirty():
            return clazz.getEps()

        innerClazzEntities = set(clazz.getMethods()) | set(clazz.getFields())
        if len(innerClazzEntities) == 0:
            return -1

        epc = self.getEntityPlacementForClass(innerClazzEntities)
        if epc == -1:
            return -1
        eps = len(innerClazzEntities) * epc
        clazz.setEps(eps)

        return eps

    def getEntityPlacementWithClassId(self, classRange):
        intermediateResult = []
        (clazzId, total) = classRange
        clazz = self.classes[clazzId]
        return self.getEntityPlacementWithClass(clazz)


    def getEntityPlacement(self):
        self.pool = Pool(processes=4)
        #self.entitySetCache.clear()

        epsTotal = 0
        epsCount = 0
        args = []
        for i in range(len(self.classes)):
            args.append((i, 0))
        
        epsSet = self.pool.map(epcHelper, args)
        for eps in epsSet:
            if eps >= 0:
                epsTotal = epsTotal + eps
                epsCount = epsCount+1
        self.pool.terminate()

        #for clazz in self.classes:
        #    eps = self.getEntityPlacementWithClass(clazz)
        #    if eps >= 0:
        #        epsTotal = epsTotal + eps
        #        epsCount = epsCount+1

        epsTotal = epsTotal / float(epsCount)
        return epsTotal


    def getCoupling(self):
        coupling = float(0)
        for clazz in self.classes:
            classCoupling = 0
            if clazz.isCouplingDirty():
                for method in clazz.getMethods():
#                for dep in method.getIncomingDeps():
#                    if (dep in clazz.getMethods()) or (dep in clazz.getFields()):
#                        pass
#                    else:
#                        coupling = coupling + 0.5
                    for dep in method.getOutgoingDeps():
                        if (dep in clazz.getMethods()) or (dep in clazz.getFields()):
                            pass
                        else:
                            classCoupling = classCoupling + 1

                for field in clazz.getFields():
#                for dep in field.getIncomingDeps():
#                    if (dep in clazz.getMethods()) or (dep in clazz.getFields()):
#                        pass
#                    else:
#                        coupling = coupling + 0.5
                    for dep in field.getOutgoingDeps():
                        if (dep in clazz.getMethods()) or (dep in clazz.getFields()):
                            pass
                        else:
                            classCoupling = classCoupling + 1

                clazz.setCoupling(classCoupling)
            else:
                classCoupling = clazz.getCoupling()

            coupling = coupling + classCoupling

        normalized_coupling = coupling / float(len(self.classes)) 
        return (normalized_coupling, coupling)
                
    def getEvalMatrix(self):
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
        #print PD.todense()
        candidateDict = {}
        (rows, cols) = PD.nonzero()
        for i in range(len(rows)):
            if rows[i] in candidateDict:
                (_, _, d) = candidateDict[rows[i]]
                if d > D[rows[i], cols[i]]:
                    candidateDict[rows[i]] = (rows[i], cols[i], D[rows[i], cols[i]])
            else:
                candidateDict[rows[i]] = (rows[i], cols[i], D[rows[i], cols[i]])
        return candidateDict
    
    def electMoveMethodBasedEPM(self):
        minEps = 1000000.0
        candidate = None
        searchSpace = 0
        for clazzIdx1 in range(len(self.classes)):
            clazz1 = self.classes[clazzIdx1]
            for method in clazz1.getMethods():
                for clazzIdx2 in range(len(self.classes)):
                    clazz2 = self.classes[clazzIdx2]
                    if clazzIdx1 != clazzIdx2:
                        clazz1.moveMethod(clazz2, method)
                        eps = self.getEntityPlacement()
                        searchSpace = searchSpace + 1
                        if (eps < minEps) or (candidate == None):
                            minEps = eps
                            candidate = (method.getIndex(), clazzIdx2, 0)
                        clazz2.moveMethod(clazz1, method)
        if candidate == None:
            return (None, 0)
        return ([candidate], searchSpace)

    def electMoveMethodBasedDM(self, D):
        candidateDict = self.getIndexOfPostiveMoveMethodCandidates(D)
        maxScore = 0
        candidate = None
        searchSpace = self.numMethod
        for methodIdx, (m, c, d) in candidateDict.iteritems():
            if d < 0 and (candidate == None or d < maxScore):
                maxScore = d
                candidate = (m, c, d)

        if candidate == None:
            return (None, 0)

        return ([candidate], searchSpace)

    def electMoveMethodSetBasedDM(self, D):
        candidateDict = self.getIndexOfPostiveMoveMethodCandidates(D)
        independentSetSet = self.getIndependentSets()
        #print "independentSetSet"
        #print independentSetSet
        maxScore = 0
        maxCandidateSet = None
        searchSpace = 0
        #print "candidateDict"
        #print candidateDict
        for independentSet in independentSetSet:
            asetScore = 0
            candidateSet = [] 
            searchSpace = searchSpace + 1
            for methodIdx in independentSet:
                if methodIdx in candidateDict:
                    (m, c, d) = candidateDict[methodIdx]
                    if d < 0:
                        asetScore = asetScore + d
                        candidateSet.append((m, c, d))
            if asetScore < maxScore:
                maxScore = asetScore
                maxCandidateSet = candidateSet
        return (maxCandidateSet, searchSpace)


    def electMoveMethodSetBasedDMwithoutDep(self, D):
        candidateDict = self.getIndexOfPostiveMoveMethodCandidates(D)
        candidateSet = []
        searchSpace = 1
        for (methodIdx, (m, c, d)) in candidateDict.items():
            if d < 0 :
                candidateSet.append((m, c, d))
        if len(candidateSet) == 0:
            return (None, 0)
        return (candidateSet, searchSpace)

    def updateMembershipMatrix(self, moveMethodSet):
        #print "Before update"
        #print self.membershipMatrix
        for (m, c, d) in moveMethodSet:
            #print self.membershipMatrix.todense()
            #print self.membershipMatrix.getrow(m).todense()
            (_, oldContainingClassIdxList) = self.membershipMatrix.getrow(m).nonzero()
            #print "oldContainingClassIdxList:",
            #print oldContainingClassIdxList
            flag = 0
            for cc in oldContainingClassIdxList:
                if self.membershipMatrix[m, cc] == 1:
                    #(norm_coupling, raw_coupling) = self.getCoupling()
                    #print "before: coupling:%d diff:%d" % ( raw_coupling, d)
                    self.membershipMatrix[m, cc] = 0

                    #print "fromIdx:",
                    #print cc,
                    #print " ",
                    #print "toIndx:",
                    #print c
                    self.membershipMatrix[m, c] = 1
                    fromClass = self.classes[cc]
                    toClass = self.classes[c]
                    movingMethod = self.entities[m]
                    fromClass.moveMethod(toClass, movingMethod)

                    #(norm_coupling, raw_coupling) = self.getCoupling()
                    #print "after: coupling:%d diff:%d" % ( raw_coupling, d)
                    #print (self.entities[m], self.classes[c], d)

                    flag = 1
                    break
                else:
                    print "membershipMatrix is broken"
                    quit()

            if flag == 0:
                continue
        #self.membershipMatrix.eliminate_zeros()
        #self.membershipMatrix.prune()
        #print "After update"
        #print "Link"
        #print self.linkMatrix.todense()
        #print "CallLink"
        #print self.callLinkMatrix.todense()
        #print "Membership"
        #print self.membershipMatrix.todense()
        #print "Class status"
        #print self.model
    def getMethodNum(self):
        return self.numMethod

    def __repr__(self):
        return self.getName()
