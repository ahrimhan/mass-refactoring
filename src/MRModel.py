import json
import os
import sys
from pprint import pprint

from MRClass import *

CURDIR = os.path.abspath(os.path.dirname(__file__))

class MRModel:
    classes = []
    entity_dict = {}
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

    def __str__(self):
        ret = ""
        for mrClass in self.classes:
            ret = ret + str(mrClass) + "\n"
        return ret



def main():
    if len(sys.argv) != 2:
        print "Usage: %s [model file]" % sys.argv[0]
        sys.exit(1)

    try:
        modelfile = sys.argv[1]
    except Exception:
        print "Usage: %s [modelfile]" % sys.argv[0]
        sys.exit(1)

    modelfile = os.path.join(CURDIR, modelfile)
    model = MRModel()
    model.load(modelfile)
    print "Model:\n"
    print "%s" % model


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print "Terminating program..."
