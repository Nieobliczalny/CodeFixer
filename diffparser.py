from diff import Diff

class DiffParser():
    OP_TYPE_APPEND = 'a'
    OP_TYPE_DELETE = 'd'
    OP_TYPE_CHANGE = 'c'

    def __init__(self):
        self.currentDiffLine = 0
        self.diffs = []
        self.parsedDiffs = []
    
    def isDiffLineAppend(self, line):
        return line[0] == '>'
    
    def isDiffLineDelete(self, line):
        return line[0] == '<'
    
    def isDiffLineHeader(self, line):
        return line[0].isdigit()
    
    def isDiffLineBreak(self, line):
        return line == '---'
    
    def isDiffOpTypeAppend(self, opType):
        return opType == self.OP_TYPE_APPEND
    
    def isDiffOpTypeChange(self, opType):
        return opType == self.OP_TYPE_CHANGE
    
    def isDiffOpTypeDelete(self, opType):
        return opType == self.OP_TYPE_DELETE
    
    def splitDiff(self, diff):
        diffText = diff.split('\n')
        diffLineNo = len(diffText)
        if diffLineNo < 2:
            return
        currentLine = 0
        currentDiff = []
        while currentLine < diffLineNo:
            line = diffText[currentLine]
            if self.isDiffLineHeader(line):
                if len(currentDiff) > 0:
                    self.diffs.append(currentDiff)
                currentDiff = []
            currentDiff.append(line)
            currentLine += 1
        
        if len(currentDiff) > 0:
            self.diffs.append(currentDiff)
    
    def parseDiff(self, diffLines):
        diff = Diff(diffLines[0])
        expectedOpType = self.OP_TYPE_DELETE
        if self.isDiffOpTypeAppend(diff.getOpType()):
            expectedOpType = self.OP_TYPE_APPEND
        for lineNo in range(1, len(diffLines)):
            line = diffLines[lineNo]
            if self.isDiffLineDelete(line) and expectedOpType == self.OP_TYPE_DELETE:
                diff.addDelete(line)
            elif self.isDiffLineBreak(line) and diff.getOpType() == self.OP_TYPE_CHANGE:
                expectedOpType = self.OP_TYPE_APPEND
            elif self.isDiffLineAppend(line) and expectedOpType == self.OP_TYPE_APPEND:
                diff.addAppend(line)
            else:
                #TODO: Implement custom errors
                raise ValueError
        return diff
    
    def getDiffs(self, diffText):
        self.splitDiff(diffText)
        for diffLines in self.diffs:
            self.parsedDiffs.append(self.parseDiff(diffLines))
        return self.parsedDiffs