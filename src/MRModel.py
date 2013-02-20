import json
import os
import sys
from pprint import pprint

from MRClass import *
from generateRandomModel import *
from MREngine import *

CURDIR = os.path.abspath(os.path.dirname(__file__))

class MRModel:
    classes = []
    entity_dict = {}

    def __init__(self):
        self.classes = []
        self.entity_dict = {}

    def load(self, filename):
        raw_data = open(filename)
        parsed_data = json.load(raw_data)
        raw_data.close()
        for class_data in parsed_data:
            mrClass = MRClass()
            mrClass.loadData(class_data, self.entity_dict)
            self.classes.append(mrClass)

        for mrClass in self.classes:
            mrClass.resolve(self.entity_dict)
    def addClass(self, mrClass):
        self.classes.append(mrClass)

    def getClasses(self):
        return self.classes

    def __str__(self):
        ret = ""
        for mrClass in self.classes:
            ret = ret + str(mrClass) + "\n"
        return ret

    def save(self, filename):
        raw_data = open(filename, "w")
        class_data_list = []
        for mrClass in self.classes:
            class_data_list.append(mrClass.saveData())
        json.dump(class_data_list, raw_data)
        raw_data.close()


def main():
    if len(sys.argv) != 3:
        print "Usage: %s [mass|step|generate] [modelfile]" % sys.argv[0]
        sys.exit(1)

    if sys.argv[1] != "mass" and sys.argv[1] != "generate" and sys.argv[1] != "step":
        print "Usage: %s [mass|step|generate] [modelfile]" % sys.argv[0]
        sys.exit(1)

    try:
        modelfile = sys.argv[2]
    except Exception:
        print "Usage: %s [mass|step|generate] [modelfile]" % sys.argv[0]
        sys.exit(1)

    modelfile = os.path.join(CURDIR, modelfile)

    if sys.argv[1] == "mass":
        model = MRModel()
        model.load(modelfile)
        engine = MREngine()
        engine.initialize(model)

        before_eps = engine.getEntityPlacement();
        before_cohesion = engine.getCohesion();
        before_coupling = engine.getCoupling();
        print "Before: cohesion:%f coupling:%f eps:%f fit:%f" % (before_cohesion, before_coupling, before_eps, before_cohesion / before_coupling)

        iteration = 0

        while True:
            D = engine.getEvalMatrix()
            (MoveMethodSet, Score) = engine.getElectMoveMethodCandidateSet(D) 
            if MoveMethodSet:
                engine.updateMembershipMatrix(MoveMethodSet)
            else:
                quit()

            after_cohesion = engine.getCohesion();
            after_coupling = engine.getCoupling();
            after_eps = engine.getEntityPlacement();
            iteration = iteration + 1
            print "Iteration %d:  cohesion:%f coupling:%f eps:%f fit:%f DScore:%f" % (iteration, after_cohesion, after_coupling, after_eps, after_cohesion / after_coupling, Score)

    if sys.argv[1] == "step":
        model = MRModel()
        model.load(modelfile)
        engine = MREngine()
        engine.initialize(model)

        before_eps = engine.getEntityPlacement();
        before_cohesion = engine.getCohesion();
        before_coupling = engine.getCoupling();
        print "Before: cohesion:%f coupling:%f eps:%f fit:%f" % (before_cohesion, before_coupling, before_eps, before_cohesion / before_coupling)

        iteration = 0

        while True:
            MoveMethod = engine.electMoveMethodBasedEPM()
            if MoveMethod:
                engine.updateMembershipMatrix([MoveMethod])
            else:
                quit()
            after_cohesion = engine.getCohesion();
            after_coupling = engine.getCoupling();
            after_eps = engine.getEntityPlacement();
            iteration = iteration + 1
            print "Iteration %d:  cohesion:%f coupling:%f eps:%f fit:%f" % (iteration, after_cohesion, after_coupling, after_eps, after_cohesion / after_coupling)

    if sys.argv[1] == "generate":
        model = generateRandomModel(3, 5, 5, 12)
        model.save(modelfile)

        model = MRModel()
        model.load(modelfile)
        engine = MREngine()
        engine.initialize(model)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print "Terminating program..."
