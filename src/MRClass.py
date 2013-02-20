from MRField import *
from MRMethod import *

class MRClass:
    name = None
    fields = []
    methods = []
    eps = 0
    epsDirty = True

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

    def addMethod(self, method):
        self.methods.append(method)

    def addField(self, field):
        self.fields.append(field)

    def removeMethod(self, method):
        self.methods.remove(method)

    def removeField(self, field):
        self.fields.remove(field)

    def moveMethod(self, other, method):
        self.setEpsDirty()
        other.setEpsDirty()
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
