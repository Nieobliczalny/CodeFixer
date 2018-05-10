#Python libs
import re

#Local modules
import ccdatabase
import cfdatabase
from config import config
from diff import Diff
from diffparser import DiffParser

class CodeExtractor():

    def __init__(self, bugData):
        self.bugData = bugData
        self.code = []
        self.diffs = []
        self.bugCodeFragment = []
        self.fixCodeFragment = []
        self.usedDiffs = []
    
    def loadCodeFromFile(self):
        with open(self.bugData.getFile(), 'r') as file:
            self.code = file.readlines()
        pass
    
    def loadCodeFromText(self, code, lineEnd = '\n', newLineEnd = '\n'):
        self.code = []
        lines = code.split(lineEnd)
        for line in lines[:-1]:
            self.code.append(line + newLineEnd)
        self.code.append(lines[-1])
    
    def loadDiff(self, diffText):
        self.diffs = DiffParser().getDiffs(diffText)
    
    def getStartLine(self):
        #Since indexing starts from 0 (line 1 is at index 0), we subtract 1
        startLine = self.bugData.getStartLine() - config.getNoOfLinesBefore() - 1
        if startLine < 0:
            startLine = 0
        return startLine
    
    def getEndLine(self):
        linesCount = len(self.code)
        #Since range end element is excluded when we use [start:end] on array
        #we do not subtract 1 so we include end line also
        endLine = self.bugData.getEndLine() + config.getNoOfLinesAfter()
        if endLine > linesCount:
            endLine = linesCount
        return endLine
    
    def extractBugCode(self):
        linesCount = len(self.code)
        if linesCount < 1:
            #TODO: Implement custom errors
            raise ValueError
        if self.bugData.getStartLine() > self.bugData.getEndLine():
            #TODO: Implement custom errors
            raise ValueError
        startLine = self.getStartLine()
        endLine = self.getEndLine()
        if startLine >= self.bugData.getStartLine() or endLine < self.bugData.getEndLine():
            #TODO: Implement custom errors
            raise ValueError
        self.bugCodeFragment = self.code[startLine:endLine]
    
    def getBugCodeFragment(self):
        return ''.join(self.bugCodeFragment)
    
    def getUsedDiffs(self):
        return self.usedDiffs
    
    def convertCodeLineToBugRelativeLine(self, codeLine, opType):
        if opType == DiffParser.OP_TYPE_APPEND:
            codeLine += 1
        codeLine -= self.getStartLine() + 1
        return codeLine
    
    def extractFixCode(self):
        if len(self.diffs) < 1:
            #TODO: Implement custom errors
            self.fixCodeFragment = []
            raise ValueError
        currentBugFragmentLine = 0
        fixCodeLines = []
        startLine = self.getStartLine()
        endLine = self.getEndLine()
        for diff in self.diffs:
            if diff.getStartLineNo() > startLine and diff.getStartLineNo() <= endLine and (diff.getStartLineNo() + len(diff.getDeletes())) <= endLine:
                self.usedDiffs.append(diff.getHeader())
                bugRelativeLineStart = self.convertCodeLineToBugRelativeLine(diff.getStartLineNo(), diff.getOpType())
                while currentBugFragmentLine < bugRelativeLineStart:
                    fixCodeLines.append(self.bugCodeFragment[currentBugFragmentLine])
                    currentBugFragmentLine += 1
                
                currentBugFragmentLine += len(diff.getDeletes())

                for append in diff.getAppends():
                    fixCodeLines.append(append[2:] + '\n')
        if len(self.usedDiffs) < 1:
            self.fixCodeFragment = []
            raise ValueError

        while currentBugFragmentLine < len(self.bugCodeFragment):
            fixCodeLines.append(self.bugCodeFragment[currentBugFragmentLine])
            currentBugFragmentLine += 1
        self.fixCodeFragment = fixCodeLines
    
    def getFixCodeFragment(self):
        return ''.join(self.fixCodeFragment)
    
    def extractAll(self, code, diff):
        self.loadCodeFromText(code)
        self.extractBugCode()
        self.loadDiff(diff)
        self.extractFixCode()
