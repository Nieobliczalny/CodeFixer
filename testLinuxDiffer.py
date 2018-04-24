import unittest

import linuxdiffer
import config

class TestLinuxDiffer(unittest.TestCase):
    def splitLinesWithRetainingLineFeed(self, text):
        lines = text.split('\n')
        for i in range(len(lines)):
            lines[i] = lines[i] + '\n'
        return lines
    
    def getFile1(self):
        return """#include <iostream>

using namespace std;

int main(void)
{
    int a;
    a = 0;
    if (a == 0)
    {
        int b = 1 / a;
        cout << b << endl;
    }
    return 0;
}"""

    def getFile2(self):
        return """#include <iostream>

using namespace std;

int main(void)
{
    int a;
    a = 0;
    if (a != 0)
    {
        int b = 1 / a;
        cout << b << endl;
    }
    return 0;
}"""

    def testDiffBetweenDifferentFiles(self):
        file1 = self.getFile1()
        file2 = self.getFile2()
        expectedOutput = """9c9
<     if (a == 0)
---
>     if (a != 0)"""
        diff = linuxdiffer.diff(file1, file2)
        self.assertEqual(expectedOutput, diff)
        file1 = """abc
"""
        file2 = """abc
cdef
"""
        expectedOutput = """1a2
> cdef"""
        diff = linuxdiffer.diff(file1, file2)
        self.assertEqual(expectedOutput, diff)
    
    def testDiffBetweenSameFiles(self):
        file1 = self.getFile1()
        file2 = self.getFile1()
        expectedOutput = ''
        diff = linuxdiffer.diff(file1, file2)
        self.assertEqual(expectedOutput, diff)
    
    def testDiffBetweenEmptyFiles(self):
        file1 = ''
        file2 = ''
        expectedOutput = ''
        diff = linuxdiffer.diff(file1, file2)
        self.assertEqual(expectedOutput, diff)
    
    def testDiffBetweenEmptyAndRegularFile(self):
        file1 = ''
        file2 = """abc
"""
        expectedOutput = """0a1
> abc"""
        diff = linuxdiffer.diff(file1, file2)
        self.assertEqual(expectedOutput, diff)
    

if __name__ == '__main__':
    unittest.main()