import unittest

from extractCode import CodeExtractor
from entities import BugData

#TODO: Extract testdata path to test config

class TestCodeExtract(unittest.TestCase):
    def getBugCodeFileMiddle(self):
        return """int main(void)
{
    int a;
    a = 3;
    a = 0;
    if (a == 0)
    {
"""

    def getCorrectBugDataFileMiddle(self):
        bugStartLine = 8
        bugEndLine = 8
        filepath = './testdata/bugcode.cpp'
        return BugData(bugStartLine, bugEndLine, filepath, '', '')
    
    def getCorrectBugDataFileBegin(self):
        bugStartLine = 1
        bugEndLine = 1
        filepath = './testdata/bugcode.cpp'
        return BugData(bugStartLine, bugEndLine, filepath, '', '')
    
    def getCorrectBugDataFileEnd(self):
        bugStartLine = 16
        bugEndLine = 16
        filepath = './testdata/bugcode.cpp'
        return BugData(bugStartLine, bugEndLine, filepath, '', '')
    
    def getCorrectBugDataFileMultiLine(self):
        bugStartLine = 7
        bugEndLine = 9
        filepath = './testdata/bugcode.cpp'
        return BugData(bugStartLine, bugEndLine, filepath, '', '')

    def getIncorrectBugDataFileNotExist(self):
        bugStartLine = 8
        bugEndLine = 8
        filepath = './testdata/bugcode_notexists.cpp'
        return BugData(bugStartLine, bugEndLine, filepath, '', '')
    
    def getIncorrectBugDataLineOutOfRange(self):
        bugStartLine = 20
        bugEndLine = 21
        filepath = './testdata/bugcode.cpp'
        return BugData(bugStartLine, bugEndLine, filepath, '', '')
    
    def getIncorrectBugDataLineBoundariesSwap(self):
        bugStartLine = 9
        bugEndLine = 7
        filepath = './testdata/bugcode.cpp'
        return BugData(bugStartLine, bugEndLine, filepath, '', '')
    
    def getFileDiff(self, lineNo, toAdd, toRemove):
        noToAdd = len(toAdd)
        noToRemove = len(toRemove)
        if noToAdd > 0 and noToRemove > 0:
            opType = 'c'
        elif noToAdd > 0:
            opType = 'a'
            lineNo -= 1
        elif noToRemove > 0:
            opType = 'd'
        else:
            raise ValueError
        fileDiff = str(lineNo) + opType + str(lineNo) + "\n"
        for lineToRemove in toRemove:
            fileDiff += "< " + lineToRemove + "\n"
        if opType == 'c':
            fileDiff += "---\n"
        for lineToAdd in toAdd:
            fileDiff += "> " + lineToAdd + "\n"
        return fileDiff[:-1]

    #Tests for extracting bugged code
    def testCodeExtractSuccess(self):
        bugData = self.getCorrectBugDataFileMiddle()
        extractor = CodeExtractor(bugData)
        extractor.loadCodeFromFile()
        extractor.extractBugCode()
        extractedCode = extractor.getBugCodeFragment()
        correctCode = self.getBugCodeFileMiddle()
        self.assertEqual(extractedCode, correctCode)

    def testCodeExtractFileBeginSuccess(self):
        bugData = self.getCorrectBugDataFileBegin()
        extractor = CodeExtractor(bugData)
        extractor.loadCodeFromFile()
        extractor.extractBugCode()
        extractedCode = extractor.getBugCodeFragment()
        correctCode = """#include <iostream>

using namespace std;

"""
        self.assertEqual(extractedCode, correctCode)

    def testCodeExtractFileEndSuccess(self):
        bugData = self.getCorrectBugDataFileEnd()
        extractor = CodeExtractor(bugData)
        extractor.loadCodeFromFile()
        extractor.extractBugCode()
        extractedCode = extractor.getBugCodeFragment()
        correctCode = """        cout << b << endl;
    }
    return 0;
}"""
        self.assertEqual(extractedCode, correctCode)

    def testCodeExtractMultiLineSuccess(self):
        bugData = self.getCorrectBugDataFileMultiLine()
        extractor = CodeExtractor(bugData)
        extractor.loadCodeFromFile()
        extractor.extractBugCode()
        extractedCode = extractor.getBugCodeFragment()
        correctCode = """
int main(void)
{
    int a;
    a = 3;
    a = 0;
    if (a == 0)
    {
        int b = 1 / a;
"""
        self.assertEqual(extractedCode, correctCode)
    
    def testCodeExtractFileNotExistFailure(self):
        bugData = self.getIncorrectBugDataFileNotExist()
        with self.assertRaises(FileNotFoundError):
            extractor = CodeExtractor(bugData)
            extractor.loadCodeFromFile()
            extractor.extractBugCode()
            extractedCode = extractor.getBugCodeFragment()
    
    def testCodeExtractLineOutOfRangeFailure(self):
        bugData = self.getIncorrectBugDataLineOutOfRange()
        with self.assertRaises(ValueError):
            extractor = CodeExtractor(bugData)
            extractor.loadCodeFromFile()
            extractor.extractBugCode()
            extractedCode = extractor.getBugCodeFragment()
    
    def testCodeExtractLineBoundariesSwapFailure(self):
        bugData = self.getIncorrectBugDataLineBoundariesSwap()
        with self.assertRaises(ValueError):
            extractor = CodeExtractor(bugData)
            extractor.loadCodeFromFile()
            extractor.extractBugCode()
            extractedCode = extractor.getBugCodeFragment()
        
    #Tests for extracting fixed code
    def testCodeFixExtractSuccessRemove(self):
        bugData = self.getCorrectBugDataFileMiddle()
        expectedFixedCode = """int main(void)
{
    int a;
    a = 0;
    if (a == 0)
    {
"""
        fileDiff = self.getFileDiff(bugData.getStartLine(), [], ['    a = 3;'])
        extractor = CodeExtractor(bugData)
        extractor.loadCodeFromFile()
        extractor.extractBugCode()
        extractor.loadDiff(fileDiff)
        extractor.extractFixCode()
        fixedCode = extractor.getFixCodeFragment()
        usedDiffs = extractor.getUsedDiffs()
        
        self.assertEqual(expectedFixedCode, fixedCode)
        self.assertEqual(1, len(usedDiffs))
        self.assertEqual('8d8', usedDiffs[0])
    
    def testCodeFixExtractSuccessAdd(self):
        bugData = self.getCorrectBugDataFileMiddle()
        expectedFixedCode = """int main(void)
{
    int a;
    a = 4;
    a = 3;
    a = 0;
    if (a == 0)
    {
"""
        fileDiff = self.getFileDiff(bugData.getStartLine(), ['    a = 4;'], [])
        extractor = CodeExtractor(bugData)
        extractor.loadCodeFromFile()
        extractor.extractBugCode()
        extractor.loadDiff(fileDiff)
        extractor.extractFixCode()
        fixedCode = extractor.getFixCodeFragment()
        usedDiffs = extractor.getUsedDiffs()
        
        self.assertEqual(expectedFixedCode, fixedCode)
        self.assertEqual(1, len(usedDiffs))
        self.assertEqual('7a7', usedDiffs[0])
    
    def testCodeFixExtractSuccessChange(self):
        bugData = self.getCorrectBugDataFileMiddle()
        expectedFixedCode = """int main(void)
{
    int a;
    a = 1;
    a = 0;
    if (a == 0)
    {
"""
        fileDiff = self.getFileDiff(bugData.getStartLine(), ['    a = 1;'], ['    a = 3;'])
        extractor = CodeExtractor(bugData)
        extractor.loadCodeFromFile()
        extractor.extractBugCode()
        extractor.loadDiff(fileDiff)
        extractor.extractFixCode()
        fixedCode = extractor.getFixCodeFragment()
        usedDiffs = extractor.getUsedDiffs()

        self.assertEqual(expectedFixedCode, fixedCode)
        self.assertEqual(1, len(usedDiffs))
        self.assertEqual('8c8', usedDiffs[0])
    
    def testCodeFixExtractSuccessAllChanges(self):
        bugData = self.getCorrectBugDataFileMiddle()
        expectedFixedCode = """int main(void)
{
    int a, b;
    b = 2;
    a = 3;
    a = 0;
    if (a != 0)
    {
"""
        fileDiff = self.getFileDiff(bugData.getStartLine() - 1, [], ['    int a;'])
        fileDiff += "\n" + self.getFileDiff(bugData.getStartLine(), ['    int a, b;', '    b = 2;'], [])
        fileDiff += "\n" + self.getFileDiff(bugData.getStartLine() + 2, ['    if (a != 0)'], ['    if (a == 0)'])

        extractor = CodeExtractor(bugData)
        extractor.loadCodeFromFile()
        extractor.extractBugCode()
        extractor.loadDiff(fileDiff)
        extractor.extractFixCode()
        fixedCode = extractor.getFixCodeFragment()
        usedDiffs = extractor.getUsedDiffs()

        self.assertEqual(expectedFixedCode, fixedCode)
        self.assertEqual(3, len(usedDiffs))
        self.assertEqual('7d7', usedDiffs[0])
        self.assertEqual('7a7', usedDiffs[1])
        self.assertEqual('10c10', usedDiffs[2])
        
    def testCodeFixExtractFailureNoDiff(self):
        bugData = self.getCorrectBugDataFileMiddle()
        bugCode = self.getBugCodeFileMiddle()
        expectedFixedCode = bugCode
        fileDiff = self.getFileDiff(bugData.getEndLine() + 20, [], ['    a = 3;'])

        extractor = CodeExtractor(bugData)
        extractor.loadCodeFromFile()
        extractor.extractBugCode()
        extractor.loadDiff(fileDiff)
        extractor.extractFixCode()
        fixedCode = extractor.getFixCodeFragment()
        usedDiffs = extractor.getUsedDiffs()

        self.assertEqual(expectedFixedCode, fixedCode)
        self.assertEqual(0, len(usedDiffs))

if __name__ == '__main__':
    unittest.main()