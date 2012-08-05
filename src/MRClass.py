from MRField import *
from MRMethod import *

class MRClass:
    name = None
    fields = []
    methods = []
    def __init__(self):
        pass

    def setName(self, name):
        self.name = name

    def getName(self):
        return name

    def addMethod(self, method):
        self.methods.append(method)

    def addField(self, field):
        self.fields.append(field)

    def removeMethod(self, method):
        self.methods.remove(method)

    def removeField(self, field):
        self.fields.remove(field)
        
    def moveMethod(self, other, method):
        other.addMethod(method)
        self.removeMethod(method)

    def getFields():
        return self.fields[:]

    def getMethods():
        return self.methods[:]

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
