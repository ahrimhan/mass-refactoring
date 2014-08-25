from MRField import *
from MRMethod import *

class MRClass:
    name = None
    fields = []
    methods = []
    eps = 0
    epsDirty = True

    cohesion = 0
    cohesionDirty = True
    
    coupling = 0
    couplingDirty = True

    def __init__(self):
        self.fields = []
        self.methods = []
        name = None

    def setName(self, name):
        self.name = name

    def getName(self):
        return self.name

    def isEpsDirty(self):
        return self.epsDirty
    def setEpsDirty(self):
        self.epsDirty = True
    def setEps(self, eps):
        self.epsDirty = False
        self.eps = eps
    def getEps(self):
        return self.eps

    def isCohesionDirty(self):
        return self.cohesionDirty
    def setCohesionDirty(self):
        self.cohesionDirty = True
    def setCohesion(self, cohesion):
        self.cohesionDirty = False
        self.cohesion = cohesion
    def getCohesion(self):
        return self.cohesion

    def isCouplingDirty(self):
        return self.couplingDirty
    def setCouplingDirty(self):
        self.couplingDirty = True
    def setCoupling(self, coupling):
        self.couplingDirty = False
        self.coupling = coupling
    def getCoupling(self):
        return self.coupling

    def addMethod(self, method):
        method.setOwner(self.getName())
        self.methods.append(method)

    def addField(self, field):
        field.setOwner(self.getName())
        self.fields.append(field)

    def removeMethod(self, method):
        self.methods.remove(method)

    def removeField(self, field):
        self.fields.remove(field)

    def moveMethod(self, other, method):
        self.setEpsDirty()
        self.setCohesionDirty()
        self.setCouplingDirty()
        other.setEpsDirty()
        other.setCohesionDirty()
        other.setCouplingDirty()
        other.addMethod(method)
        if method in self.methods:
            self.removeMethod(method)
        else:
            print "there are no method"
            print self.methods
            print self.fields
            print method
            quit()

    def getFields(self):
        return self.fields

    def getMethods(self):
        return self.methods

    def removeSetter(self):
        for mrMethod in self.methods[:]:
            methodShortName = mrMethod.getName().split(":", 1)[0]
            methodShortName = methodShortName.rsplit(".", 1)[-1]
            if methodShortName.startswith("set"):
                if len(mrMethod.getOutgoingDeps()) < 4:
                    for dep in list(mrMethod.getOutgoingDeps()):
                        if not dep.isMethod():
                            removename = methodShortName[3:].lower()
                            if dep.getName().lower().find(removename) != -1:
                                self.methods.remove(mrMethod)
                                #print "%s <- %s  <<%s, %s<<" %( dep.getName(), mrMethod.getName(), methodShortName, removename )
                                for indep in mrMethod.getIncomingDeps():
                                    dep.addIncomingDep(indep)
                                break
                elif len(mrMethod.getOutgoingDeps()) == 0:
                    self.methods.remove(mrMethod)

            elif methodShortName.startswith("get"):
                if len(mrMethod.getOutgoingDeps()) < 4:
                    for dep in list(mrMethod.getOutgoingDeps()):
                        if not dep.isMethod():
                            removename = methodShortName[3:].lower()
                            if dep.getName().lower().find(removename) != -1:
                                self.methods.remove(mrMethod)
                                #print "%s <- %s  >>%s, %s>>" %( dep.getName(), mrMethod.getName(), methodShortName, removename )
                                for indep in mrMethod.getIncomingDeps():
                                    dep.addIncomingDep(indep)
                                break
                elif len(mrMethod.getOutgoingDeps()) == 0:
                    self.methods.remove(mrMethod)

    def loadData(self, class_data, entity_dict):
        self.setName(class_data["name"])
        self.fields = []
        for field_data in class_data["fields"]:
                mrField = MRField()
                mrField.loadData(field_data, entity_dict)
                self.addField(mrField)
        self.methods = []
        for method_data in class_data["methods"]:
                mrMethod = MRMethod()
                mrMethod.loadData(method_data, entity_dict)
                self.addMethod(mrMethod)

    def saveData(self):
        fields_data = []
        methods_data = []
        for mrField in self.fields:
            fields_data.append(mrField.saveData())
        for mrMethod in self.methods:
            methods_data.append(mrMethod.saveData())
        class_data = {"name": self.getName(), "fields":fields_data, "methods":methods_data}
        return class_data

    def resolve(self, entity_dict):
        for mrField in self.fields:
            mrField.resolve(entity_dict)
        for mrMethod in self.methods:
            mrMethod.resolve(entity_dict)

    def __str__(self):
        ret = "class " + self.name + " {\n"
        for mrField in self.fields:
            ret = ret + str(mrField) + "\n"
        for mrMethod in self.methods:
            ret = ret + str(mrMethod) + "\n"
        ret = ret + "}\n"
        return ret

    def __repr__(self):
        return self.getName()
    def __hash__(self):
        return hash(self.name)
    def __eq__(self, other):
        return self.name == other.name
