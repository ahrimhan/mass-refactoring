from MREntity import *

class MRMethod(MREntity):
    def isMovable(self):
        return True
    def isMethod(self):
        return True
    def __str__(self):
        ret = "\tmethod "
        ret = ret + self.getName() + " {\n"
        for dep in self.incomingDeps:
            ret = ret + "\t\t<- " + dep.getName() + "\n"
        for dep in self.outgoingDeps:
            ret = ret + "\t\t-> " + dep.getName() + "\n"
        ret = ret + "\t}\n"
        return ret
    def __repr__(self):
        return self.getName()
    def __hash__(self):
        return hash(self.name)
    def __eq__(self, other):
        return self.name == other.name
