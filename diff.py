import re

class Diff():
    def __init__(self, line):
        self.header = line
        (startLineNo, opType) = self.parseDiffHeader(self.header)
        self.opType = opType
        self.startLineNo = startLineNo
        self.appends = []
        self.deletes = []
    
    def parseDiffHeader(self, header):
        regexMatch = re.search('^([0-9]+)(,[0-9]+)?([acd])([0-9]+)(,[0-9]+)?$', header)
        if regexMatch is None:
            #TODO: Implement custom errors
            raise ValueError
        return (int(regexMatch.group(1)), regexMatch.group(3))

    def addAppend(self, line):
        self.appends.append(line)
    
    def addDelete(self, line):
        self.deletes.append(line)
    
    def getOpType(self):
        return self.opType
    
    def getHeader(self):
        return self.header
    
    def getStartLineNo(self):
        return self.startLineNo
    
    def getAppends(self):
        return self.appends
    
    def getDeletes(self):
        return self.deletes