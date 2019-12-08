from config import config
import json

class Dictionary():
    def __init__(self, checker):
        self.dictionary = []
        with open(config.cfDictFilenameFormat.format(checker), "r") as f:
            fileData = f.read()
            self.dictionary = json.loads(fileData)
            #self.dictionary.sort()
            self.sort()
            print(self.dictionary)
    def index(self, value):
        if not self.contains(value):
            return -1
        return self.dictionary.index(value)
    def contains(self, value):
        return (value in self.dictionary)
    def get(self, index):
        return self.dictionary[index]
    def length(self):
        return len(self.dictionary)
    def sort(self):
        tokens = [int(x[2:]) for x in self.dictionary if x.startswith("T_")]
        unks = [int(x[4:]) for x in self.dictionary if x.startswith("UNK_")]
        rest = [x for x in self.dictionary if not (x.startswith("T_") or x.startswith("UNK_"))]
        tokens.sort()
        unks.sort()
        rest.sort()
        dictionary = []
        for t in tokens:
            dictionary.append("T_{0}".format(t))
        for u in unks:
            dictionary.append("UNK_{0}".format(u))
        for r in rest:
            dictionary.append(r)
        self.dictionary = dictionary