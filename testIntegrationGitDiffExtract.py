import unittest

import posixdiffer
import gitprovider
from extractCode import CodeExtractor
import config
import random
import string
from entities import BugData

class TestIntegrationGitDiffExtract(unittest.TestCase):
    def splitLinesWithRetainingLineFeed(self, text):
        lines = text.split('\n')
        for i in range(len(lines)):
            lines[i] = lines[i] + '\n'
        return lines

    def getBugData(self):
        bugStartLine = 8
        bugEndLine = 8
        filepath = 'bugcode2.cpp'
        return BugData(bugStartLine, bugEndLine, filepath, '')
    
    def getRandomName(self):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    
    def testDiffBetweenTwoCommits(self):
        gp = gitprovider.GitProvider(config.test_repo)
        commits = gp.getAllVersions('master')
        commit1 = commits[-2]
        commit2 = commits[-3]
        file1 = gp.getFileContents('bugcode2.cpp', commit1)
        file2 = gp.getFileContents('bugcode2.cpp', commit2)
        diff = posixdiffer.diff(self.splitLinesWithRetainingLineFeed(file1), self.splitLinesWithRetainingLineFeed(file2))
        expectedOutput = """8d7
<     a = 3;\r"""
        self.assertEqual(expectedOutput, diff)
    
    def testExtractCodeWithDiffBetweenTwoCommits(self):
        gp = gitprovider.GitProvider(config.test_repo)
        commits = gp.getAllVersions('master')
        commit1 = commits[-2]
        commit2 = commits[-3]
        file1 = gp.getFileContents('bugcode2.cpp', commit1)
        file2 = gp.getFileContents('bugcode2.cpp', commit2)
        diff = posixdiffer.diff(self.splitLinesWithRetainingLineFeed(file1), self.splitLinesWithRetainingLineFeed(file2))
        usedDiffs = []
        bugData = self.getBugData()
        extractor = CodeExtractor(bugData)
        extractor.loadCodeFromText(file1, '\r\n', '\n')
        extractor.extractBugCode()
        extractor.loadDiff(diff)
        extractor.extractFixCode()
        bugCode = extractor.getBugCodeFragment()
        fixCode = extractor.getFixCodeFragment()
        usedDiffs = extractor.getUsedDiffs()
        expectedOutputFix = """int main(void)
{
    int a;
    a = 0;
    if (a == 0)
    {
"""
        expectedOutputBug = """int main(void)
{
    int a;
    a = 3;
    a = 0;
    if (a == 0)
    {
"""
        self.assertEqual(expectedOutputBug, bugCode)
        self.assertEqual(expectedOutputFix, fixCode)
        self.assertEqual(1, len(usedDiffs))
    

if __name__ == '__main__':
    unittest.main()