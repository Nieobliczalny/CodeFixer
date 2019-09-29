from cfdatabase import CFDatabase
from config import config
from cxxlexer import CxxLexer

class ModelDataBuilder():
    def __init__(self):
        self.db = CFDatabase(config.getCfDbFile())
        self.lexer = CxxLexer()
        self.dictionary = {"id": 1, "data": []}
    
    def buildDictionary(self):
        self.dictionary = {"id": 1, "data": []}
        for codeSnippet in self.data:
            for token in codeSnippet:
                self.addToDictionary(token)
    
    def setDictionary(self, dictionary):
        self.dictionary = dictionary
    
    def getDictionary(self):
        return self.dictionary
    
    def addToDictionary(self, token):
        if not self.isInDictionary(token):
            self.dictionary['data'].append({"token": token['token'], "value": token['value'], "id": self.dictionary['id']})
            self.dictionary['id'] += 1

    def isInDictionary(self, token):
        return self.findInDictionary(token) > -1
    
    def findInDictionary(self, token):
        if not token['has_value']:
            token['value'] = None
        for t in self.dictionary['data']:
            if t['token'] == token['token'] and t['value'] == token['value']:
                return t['id']
        return -1
    
    def fetchFixData(self, checker):
        self.rawData = self.db.getFixDataForChecker(checker)
        if len(self.rawData) < 1:
            print("No data found.")
            raise ValueError
        self.data = [self.lexer.tokenize(x[2]) for x in self.rawData]

    def fetchBugData(self, checker):
        self.rawData = self.db.getFixDataForChecker(checker)
        if len(self.rawData) < 1:
            print("No data found.")
            raise ValueError
        self.data = [self.lexer.tokenize(x[1]) for x in self.rawData]
    
    def encodeData(self, data):
        vector = []
        for token in data:
            id = self.findInDictionary(token)
            if id < 0:
                self.addToDictionary(token)
                id = self.findInDictionary(token)
            vector.append(id)
        return vector
    
    def getEncodedFixData(self, checker, dictionary = None):
        self.fetchFixData(checker)
        return self.getEncodedData(checker, dictionary)

    def getEncodedBugData(self, checker, dictionary = None):
        self.fetchBugData(checker)
        return self.getEncodedData(checker, dictionary)

    def getEncodedData(self, checker, dictionary):
        if dictionary is None:
            self.buildDictionary()
        else:
            self.setDictionary(dictionary)
        self.dataVector = [self.encodeData(d) for d in self.data]
        return self.dataVector
    
    def decodeData(self, data):
        tokens = []
        for value in data:
            tokenData = self.dictionary.data[value - 1]
            token = {"token": tokenData['token']}
            if tokenData['value'] is None:
                token['has_value'] = False
            else:
                token['has_value'] = True
                token['value'] = tokenData['value']
            tokens.append(token)
        return tokens
    
    def detokenize(self, input, output):
        pass