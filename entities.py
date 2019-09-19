class BugData():
    def __init__(self, startLine, endLine, file, checker, status, message, line):
        self.startLine = startLine
        self.endLine = endLine
        self.file = file
        self.checker = checker
        self.status = status
        self.message = message
        self.line = line
    
    def getStartLine(self):
        return self.startLine
    
    def getEndLine(self):
        return self.endLine
    
    def getFile(self):
        return self.file
    
    def getMessage(self):
        return self.message
    
    def getLine(self):
        return self.line
    
    def getChecker(self):
        return self.checker
    
    def getStatus(self):
        return self.status

class FixData():
    def __init__(self, bugCode, fixCode, checker, message, line):
        self.bugCode = bugCode
        self.fixCode = fixCode
        self.checker = checker
        self.message = message
        self.line = line
    
    def getBugCode(self):
        return self.bugCode
    
    def getFixCode(self):
        return self.fixCode
    
    def getChecker(self):
        return self.checker
    
    def getMessage(self):
        return self.message
    
    def getLine(self):
        return self.line