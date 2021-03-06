
def if_else(condition, a, b) :
    if condition : return a
    else         : return b

class MREntity:
    name = None
    incomingDeps = set()
    outgoingDeps = set()
    incomingDepsIndices = set()
    idil = 0
    outgoingDepsIndices = set()
    odil = 0
    index = 0
    owner = None

    def __init__(self):
        self.incomingDeps = set()
        self.outgoingDeps = set()
        self.incomingDepsIndices = set()
        self.outgoingDepsIndices = set()

    def setName(self, name):
        self.name = name

    def getName(self):
        return self.name

    def isMethod(self):
        return False

    def isMovable(self):
        return False

    def setIndex(self, index):
        self.index = index

    def getIndex(self):
        return self.index

    def addIncomingDep(self, dep):
        self.incomingDeps.add(dep)

    def removeIncomingDep(self, dep):
        self.incomingDeps.remove(dep)

    def addOutgoingDep(self, dep):
        self.outgoingDeps.add(dep)

    def removeOutgoingDep(self, dep):
        self.outgoingDeps.remove(dep)

    def getIncomingDeps(self):
        return self.incomingDeps

    def getIncomingDepsIndices(self):
        return (self.incomingDepsIndices, self.idil)

    def getOutgoingDeps(self):
        return self.outgoingDeps

    def getOutgoingDepsIndices(self):
        return (self.outgoingDepsIndices, self.odil)

    def setOwner(self, owner):
        self.owner = owner

    def getOwner(self):
        return self.owner

    def resolve(self, entity_dict):
        self.incomingDeps= self.resolve_entity(self.incomingDeps, entity_dict)
        self.outgoingDeps= self.resolve_entity(self.outgoingDeps, entity_dict)

    def resolve_entity(self, depList, entity_dict):
        retDepList = set()
        for dep in depList:
            if dep in entity_dict:
                retDepList.add(entity_dict[dep])
        return retDepList

    def resetDepIndices(self):
        self.incomingDepsIndices.clear()
        self.outgoingDepsIndices.clear()
        for incomingDep in self.incomingDeps:
            self.incomingDepsIndices.add(incomingDep.getIndex())
        for outgoingDep in self.outgoingDeps:
            self.outgoingDepsIndices.add(outgoingDep.getIndex())
        self.idil = len(self.incomingDepsIndices)
        self.odil = len(self.outgoingDepsIndices)

    def loadData(self, entity_data, entity_dict):
        self.setName(entity_data["name"])
        entity_dict[self.name] = self
        self.incomingDeps = set()
        self.outgoingDeps = set()
        if "incomingDeps" in entity_data:
            for incoming_entity in entity_data["incomingDeps"]:
                self.addIncomingDep(incoming_entity)
        if "outgoingDeps" in entity_data:
            for outgoing_entity in entity_data["outgoingDeps"]:
                self.addOutgoingDep(outgoing_entity)

    def saveData(self):
        incoming_data = []
        outgoing_data = []
        for incomingDep in self.incomingDeps:
            incoming_data.append(incomingDep.getName())
        for outgoingDep in self.outgoingDeps:
            outgoing_data.append(outgoingDep.getName())
        entity_data = {"name" : self.getName(), "incomingDeps":incoming_data, "outgoingDeps":outgoing_data}
        return entity_data
