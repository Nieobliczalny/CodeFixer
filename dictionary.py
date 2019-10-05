from config import config
import json

class Dictionary():
    def __init__(self, checker):
        self.dictionary = []
        with open(config.cfDictFilenameFormat.format(checker), "r") as f:
            fileData = f.read()
            self.dictionary = json.loads(fileData)
            self.dictionary.sort()
    def index(self, value):
        return self.dictionary.index(value)
    def contains(self, value):
        return (value in self.dictionary)
    def get(self, index):
        return self.dictionary[index]
    def length(self):
        return len(self.dictionary)