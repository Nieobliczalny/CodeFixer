import unittest

import posixdiffer
import config

class TestPosixDiffer(unittest.TestCase):
    def splitLinesWithRetainingLineFeed(self, text):
        lines = text.split('\n')
        for i in range(len(lines) - 1):
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
        diff = posixdiffer.diff(self.splitLinesWithRetainingLineFeed(file1), self.splitLinesWithRetainingLineFeed(file2))
        self.assertEqual(expectedOutput, diff)
    
    def testDiffBetweenSameFiles(self):
        file1 = self.getFile1()
        file2 = self.getFile1()
        expectedOutput = ''
        diff = posixdiffer.diff(self.splitLinesWithRetainingLineFeed(file1), self.splitLinesWithRetainingLineFeed(file2))
        self.assertEqual(expectedOutput, diff)
    

if __name__ == '__main__':
    unittest.main()