class BugData():
    def __init__(self, startLine, endLine, file, checker):
        self.startLine = startLine
        self.endLine = endLine
        self.file = file
        self.checker = checker
    
    def getStartLine(self):
        return self.startLine
    
    def getEndLine(self):
        return self.endLine
    
    def getFile(self):
        return self.file
    
    def getChecker(self):
        return self.checker

class FixData():
    def __init__(self, bugCode, fixCode, checker):
        self.bugCode = bugCode
        self.fixCode = fixCode
        self.checker = checker
    
    def getBugCode(self):
        return self.bugCode
    
    def getFixCode(self):
        return self.fixCode
    
    def getChecker(self):
        return self.checker