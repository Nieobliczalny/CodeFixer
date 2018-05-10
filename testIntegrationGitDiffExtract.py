import unittest

from linuxdiffer import LinuxDiffer
import gitprovider
from extractCode import CodeExtractor
from config import config
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
        return BugData(bugStartLine, bugEndLine, filepath, '', '')

    def getBugData2(self):
        bugStartLine = 12
        bugEndLine = 12
        filepath = 'bugcode2.cpp'
        return BugData(bugStartLine, bugEndLine, filepath, '', '')
    
    def getRandomName(self):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    
    def testDiffBetweenTwoCommits(self):
        gp = gitprovider.GitProvider(config.getRepoDir())
        commits = gp.getAllVersions('master')
        commit1 = commits[-2]
        commit2 = commits[-3]
        file1 = gp.getFileContents('bugcode2.cpp', commit1)
        file2 = gp.getFileContents('bugcode2.cpp', commit2)
        diff = LinuxDiffer().diff(file1, file2)
        expectedOutput = """8d7
<     a = 3;"""
        self.assertEqual(expectedOutput, diff)
    
    def testExtractCodeWithDiffBetweenTwoCommits(self):
        gp = gitprovider.GitProvider(config.getRepoDir())
        commits = gp.getAllVersions('master')
        commit1 = commits[-2]
        commit2 = commits[-3]
        file1 = gp.getFileContents('bugcode2.cpp', commit1)
        file2 = gp.getFileContents('bugcode2.cpp', commit2)
        diff = LinuxDiffer().diff(file1, file2)
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
    
    def testExtractCodeWithEmptyDiffBetweenTwoCommits(self):
        gp = gitprovider.GitProvider(config.getRepoDir())
        commits = gp.getAllVersions('master')
        commit1 = commits[-2]
        commit2 = commits[-2]
        file1 = gp.getFileContents('bugcode2.cpp', commit1)
        file2 = gp.getFileContents('bugcode2.cpp', commit2)
        diff = LinuxDiffer().diff(file1, file2)
        usedDiffs = []
        bugData = self.getBugData()
        extractor = CodeExtractor(bugData)
        extractor.loadCodeFromText(file1, '\r\n', '\n')
        extractor.extractBugCode()
        extractor.loadDiff(diff)
        with self.assertRaises(ValueError):
            extractor.extractFixCode()
        bugCode = extractor.getBugCodeFragment()
        fixCode = extractor.getFixCodeFragment()
        usedDiffs = extractor.getUsedDiffs()
        expectedOutputFix = ''
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
        self.assertEqual(0, len(usedDiffs))
    
    def testExtractCodeWithDiffBetweenTwoCommitsNotRelatedToBug(self):
        gp = gitprovider.GitProvider(config.getRepoDir())
        commits = gp.getAllVersions('master')
        commit1 = commits[-2]
        commit2 = commits[-3]
        file1 = gp.getFileContents('bugcode2.cpp', commit1)
        file2 = gp.getFileContents('bugcode2.cpp', commit2)
        diff = LinuxDiffer().diff(file1, file2)
        usedDiffs = []
        bugData = self.getBugData2()
        extractor = CodeExtractor(bugData)
        extractor.loadCodeFromText(file1, '\r\n', '\n')
        extractor.extractBugCode()
        extractor.loadDiff(diff)
        with self.assertRaises(ValueError):
            extractor.extractFixCode()
        bugCode = extractor.getBugCodeFragment()
        fixCode = extractor.getFixCodeFragment()
        usedDiffs = extractor.getUsedDiffs()
        expectedOutputFix = ''
        expectedOutputBug = """    a = 0;
    if (a == 0)
    {
        int b = 1 / a;
        cout << b << endl;
    }
    return 0;
"""
        self.assertEqual(expectedOutputBug, bugCode)
        self.assertEqual(expectedOutputFix, fixCode)
        self.assertEqual(0, len(usedDiffs))
    

if __name__ == '__main__':
    unittest.main()