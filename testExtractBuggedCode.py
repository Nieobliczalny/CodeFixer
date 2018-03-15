import unittest

import extractCode

class TestCodeExtract(unittest.TestCase):
    def getCorrectBugDataFileMiddle(self):
        bugStartLine = 8
        bugEndLine = 8
        filepath = 'testdata/bugcode.cpp'
        return (bugStartLine, 0, bugEndLine, 0, filepath)
    
    def getCorrectBugDataFileBegin(self):
        bugStartLine = 1
        bugEndLine = 1
        filepath = 'testdata/bugcode.cpp'
        return (bugStartLine, 0, bugEndLine, 0, filepath)
    
    def getCorrectBugDataFileEnd(self):
        bugStartLine = 16
        bugEndLine = 16
        filepath = 'testdata/bugcode.cpp'
        return (bugStartLine, 0, bugEndLine, 0, filepath)
    
    def getCorrectBugDataFileMultiLine(self):
        bugStartLine = 7
        bugEndLine = 9
        filepath = 'testdata/bugcode.cpp'
        return (bugStartLine, 0, bugEndLine, 0, filepath)

    def getIncorrectBugDataFileNotExist(self):
        bugStartLine = 8
        bugEndLine = 8
        filepath = 'testdata/bugcode_notexists.cpp'
        return (bugStartLine, 0, bugEndLine, 0, filepath)
    
    def getIncorrectBugDataLineOutOfRange(self):
        bugStartLine = 20
        bugEndLine = 21
        filepath = 'testdata/bugcode.cpp'
        return (bugStartLine, 0, bugEndLine, 0, filepath)
    
    def getIncorrectBugDataLineBoundariesSwap(self):
        bugStartLine = 9
        bugEndLine = 7
        filepath = 'testdata/bugcode.cpp'
        return (bugStartLine, 0, bugEndLine, 0, filepath)

    def testCodeExtractSuccess(self):
        bugData = self.getCorrectBugDataFileMiddle()
        extractedCode = extractCode.extractBugCode(bugData)
        correctCode = """int main(void)
{
    int a;
    a = 3;
    a = 0;
    if (a == 0)
    {
"""
        self.assertEqual(extractedCode, correctCode)

    def testCodeExtractFileBeginSuccess(self):
        bugData = self.getCorrectBugDataFileBegin()
        extractedCode = extractCode.extractBugCode(bugData)
        correctCode = """#include <iostream>

using namespace std;

"""
        self.assertEqual(extractedCode, correctCode)

    def testCodeExtractFileEndSuccess(self):
        bugData = self.getCorrectBugDataFileEnd()
        extractedCode = extractCode.extractBugCode(bugData)
        correctCode = """        cout << b << endl;
    }
    return 0;
}"""
        self.assertEqual(extractedCode, correctCode)

    def testCodeExtractMultiLineSuccess(self):
        bugData = self.getCorrectBugDataFileMultiLine()
        extractedCode = extractCode.extractBugCode(bugData)
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
            extractedCode = extractCode.extractBugCode(bugData)
    
    def testCodeExtractLineOutOfRangeFailure(self):
        bugData = self.getIncorrectBugDataLineOutOfRange()
        with self.assertRaises(ValueError):
            extractedCode = extractCode.extractBugCode(bugData)
    
    def testCodeExtractLineBoundariesSwapFailure(self):
        bugData = self.getIncorrectBugDataLineBoundariesSwap()
        print(bugData)
        with self.assertRaises(ValueError):
            extractedCode = extractCode.extractBugCode(bugData)
        

if __name__ == '__main__':
    unittest.main()