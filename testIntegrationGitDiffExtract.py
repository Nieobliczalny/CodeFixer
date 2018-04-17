import unittest

import posixdiffer
import gitprovider
import extractCode
import config
import random
import string

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
        return [bugStartLine, 0, bugEndLine, 0, filepath]
    
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
        bugData[4] = config.tmpDir + '/' + self.getRandomName()
        with open(bugData[4], 'w') as file:
            file.write(file1)
        bugCode = extractCode.extractBugCode(bugData)
        fixCode = extractCode.extractFixCode(bugData, bugCode, diff, usedDiffs)
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
    

if __name__ == '__main__':
    unittest.main()