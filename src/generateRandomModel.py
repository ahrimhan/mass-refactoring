from MRModel import *
from MRClass import *
from MRField import *
from MRMethod import *
import random


def generateRandomModel(classNum, methodNum, fieldNum, depNum):
    newMethodList = []
    newFieldList = []
    newEntityList = []
    newModel = MRModel()
    random.seed()

    print "classes are created...",
    for c in range(classNum):
        newClass = MRClass()
        newClass.setName("Class"+str(c))
        newModel.addClass(newClass)
    print "done"

    print "methods are created...",
    for m in range(methodNum):
        newMethod = MRMethod()
        newMethod.setName("Method"+str(m))
        newMethodList.append(newMethod)
        newEntityList.append(newMethod)
    print "done"


    print "fields are created...",
    for f in range(fieldNum):
        newField = MRField()
        newField.setName("Field"+str(f))
        newFieldList.append(newField)
        newEntityList.append(newField)
    print "done"


    print "dependencies are created...",

    for method in newMethodList:
        fieldIdx = random.randint(0, len(newFieldList) - 1)
        method.addOutgoingDep(newFieldList[fieldIdx])
        newFieldList[fieldIdx].addIncomingDep(method)

    for d in range(depNum):
        while True:
            methodIdx1 = random.randint(0, len(newMethodList) - 1)
            entityIdx2 = random.randint(0, len(newEntityList) - 1)
            if newEntityList[entityIdx2] in newMethodList[methodIdx1].getOutgoingDeps():
                continue
            else:
                break
        print "(%d -> %d) dep %d: %s(%d) -> %s(%d)" % (methodIdx1, entityIdx2, d, newMethodList[methodIdx1].getName(), len(newMethodList[methodIdx1].getOutgoingDeps()), newEntityList[entityIdx2].getName(), len(newEntityList[entityIdx2].getOutgoingDeps()))
        newMethodList[methodIdx1].addOutgoingDep(newEntityList[entityIdx2])
        newEntityList[entityIdx2].addIncomingDep(newMethodList[methodIdx1])
    print "done"

    print "fields and methods are located to classes...",
    while len(newEntityList) > 0:
        classIdx = random.randint(0, len(newModel.getClasses()) - 1)
        entityIdx = random.randint(0, len(newEntityList) - 1)
        c = newModel.getClasses()[classIdx]
        if isinstance(newEntityList[entityIdx], MRField):
            c.addField(newEntityList[entityIdx])
        else:
            c.addMethod(newEntityList[entityIdx])
        newEntityList.pop(entityIdx)
    print "done"


    return newModel

