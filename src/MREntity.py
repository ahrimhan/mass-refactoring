
def if_else(condition, a, b) :
    if condition : return a
    else         : return b

class MREntity:
    name = None
    incomingDeps = []
    outgoingDeps = []

    def __init__(self):
        self.incomingDeps = []
        self.outgoingDeps = []

    def setName(self, name):
        self.name = name

    def getName(self):
        return self.name

    def isMovable(self):
        return False

    def addIncomingDep(self, dep):
        self.incomingDeps.append(dep)

    def removeIncomingDep(self, dep):
        self.incomingDeps.remove(dep)

    def addOutgoingDep(self, dep):
        self.outgoingDeps.append(dep)

    def removeOutgoingDep(self, dep):
        self.outgoingDeps.remove(dep)

    def getIncomingDeps(self):
        return self.incomingDeps

    def getOutgoingDeps(self):
        return self.outgoingDeps

    def resolve(self, entity_dict):
        self.incomingDeps= self.resolve_entity(self.incomingDeps, entity_dict)
        self.outgoingDeps= self.resolve_entity(self.outgoingDeps, entity_dict)

    def resolve_entity(self, depList, entity_dict):
        retDepList = []
        for dep in depList:
            if dep in entity_dict:
                retDepList.append(entity_dict[dep])
        return retDepList

    def loadData(self, entity_data, entity_dict):
        self.setName(entity_data["name"])
        entity_dict[self.name] = self
        self.incomingDeps = []
        self.outgoingDeps = []
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
