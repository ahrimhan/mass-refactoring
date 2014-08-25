import json
import os
import sys
from pprint import pprint

from MRClass import *
from generateRandomModel import *
from MREngine import *
import time
import resource
import datetime
import thread

CURDIR = os.path.abspath(os.path.dirname(__file__))

global loop
loop = True

def using(point=""):
    usage=resource.getrusage(resource.RUSAGE_SELF)
    return '''%s: maxrss=%f ixrss=%f idrss=%f isrss=%f
           '''%(point,usage[2]/1000000.0,usage[3]/1000000.0, usage[4]/1000000.0, usage[5]/1000000.0 )

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

        for mrClass in self.classes:
            mrClass.removeSetter()

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

def monitorThreadFunc():
    global loop
    while loop:
        print >> sys.stderr, using(str(datetime.datetime.now()))
        time.sleep(1)


def main():
    refactoring_args = ["mass-with-dep", "mass-without-dep", "step-epm", "step-dm"]
    if len(sys.argv) != 3 or (sys.argv[1] != "generate" and (not (sys.argv[1] in refactoring_args))):
        print "Usage: %s [mass-with-dep|mass-without-dep|step-epm|step-dm|generate] [modelfile]" % sys.argv[0]
        sys.exit(1)

    modelfile = sys.argv[2]

    modelfile = os.path.join(CURDIR, modelfile)
    start_time = time.time()

    thread.start_new_thread(monitorThreadFunc, ())

    if sys.argv[1] in refactoring_args:
        refactoring_type = sys.argv[1]
        model = MRModel()
        model.load(modelfile)
        engine = MREngine()
        engine.initialize(model)

        #before_eps = engine.getEntityPlacement();
        (before_cohesion, raw_cohesion, cohesionClassCount) = engine.getCohesion();
        (before_coupling, raw_coupling) = engine.getCoupling();
        #print "Before: cohesion:%f coupling:%f raw_coupling:%f fit:%f" % (before_cohesion, before_coupling, raw_coupling, before_cohesion / before_coupling),
        print "Iter\tMSC\tMPC\tFit\tRefactoring #\tRef Accumulated #\texpected coupling\tactual coupling\tsearch space\telapsed time\texhaustive space"
        print "%d\t%.10f\t%.10f\t%.10f\t%d\t%d\t%d\t%d\t%d\t%.2f" % (0, before_cohesion, before_coupling, before_cohesion / before_coupling, 0, 0, 0, raw_coupling, 0, 0)# exhaustiveSpace)
        print ""

        iteration = 0
        refactoring_total = 0
        searchSpace = 0
        expected_coupling = raw_coupling
        exhaustiveSpace = 0
        moveMethodSetLen = 0

        while True:
            #electAndUpdateTime = time.time()

            if refactoring_type == "mass-with-dep":
                D = engine.getEvalMatrix()
                (MoveMethodSet, ss) = engine.electMoveMethodSetBasedDM(D)
            elif refactoring_type == "mass-without-dep":
                D = engine.getEvalMatrix()
                (MoveMethodSet, ss) = engine.electMoveMethodSetBasedDMwithoutDep(D)
            elif refactoring_type == "step-epm":
                (MoveMethodSet, ss) = engine.electMoveMethodBasedEPM()
            elif refactoring_type == "step-dm":
                D = engine.getEvalMatrix()
                (MoveMethodSet, ss) = engine.electMoveMethodBasedDM(D)

            #electAndUpdateTime = time.time() - electAndUpdateTime
            #print "elect time:%.3f" % electAndUpdateTime
            #electAndUpdateTime = time.time()

            searchSpace = searchSpace + ss

            print "----------- move method set------------ "
            print MoveMethodSet

            if MoveMethodSet:
                engine.updateMembershipMatrix(MoveMethodSet)
            else:
                break

            #electAndUpdateTime = time.time() - electAndUpdateTime
            #print "update time:%.3f" % electAndUpdateTime

            refactoring_total = refactoring_total + len(MoveMethodSet)
            iteration = iteration + 1
            moveMethodSetLen = len(MoveMethodSet)

            #if iteration % 10 == 0 or not (refactoring_type == "step-dm"):
            (after_cohesion, raw_cohesion, cohesionClassCount) = engine.getCohesion();
            (after_coupling, raw_coupling) = engine.getCoupling();
            #(after_cohesion, raw_cohesion, cohesionClassCount) = (1, 1, 1)
            #(after_coupling, raw_coupling) = (1, 1)

            for (m, c, d) in MoveMethodSet:
                expected_coupling = expected_coupling + d

            #after_eps = engine.getEntityPlacement();

            #exhaustiveSpace = exhaustiveSpace + (engine.getMethodNum() ** iteration)

            print "%d\t%.10f\t%.10f\t%.10f\t%d\t%d\t%d\t%d\t%d\t%.2f" % (iteration, after_cohesion, after_coupling, after_cohesion / after_coupling, moveMethodSetLen, refactoring_total, expected_coupling, raw_coupling, searchSpace, (time.time() - start_time))# exhaustiveSpace)


            if iteration >= 10000:
                break
        
        #if (iteration % 10) != 0 and refactoring_type == "step-dm":
        #    print "%d\t%.10f\t%.10f\t%.10f\t%d\t%d\t%d\t%d\t%d\t%.2f" % (iteration, after_cohesion, after_coupling, after_cohesion / after_coupling, moveMethodSetLen, refactoring_total, expected_coupling, raw_coupling, searchSpace, (time.time() - start_time))# exhaustiveSpace)

    loop = False
    if sys.argv[1] == "generate":
        #model = generateRandomModel(25, 200, 120, 1000)
        model = generateRandomModel(5, 5, 5, 20)
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
