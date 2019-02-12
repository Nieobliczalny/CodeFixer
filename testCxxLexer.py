import unittest

from cxxlexer import CxxLexer

class TestCxxLexer(unittest.TestCase):
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
    def getTokens1(self):
        return [{u"token": u"315", u"has_value": False}, {u"token": u"289", u"has_value": False}, {u"token": u"347", u"has_value": True, u"value": u"std"}, {u"token": u"59", u"has_value": False}, {u"token": u"286", u"has_value": False}, {u"token": u"347", u"has_value": True, u"value": u"main"}, {u"token": u"40", u"has_value": False}, {u"token": u"317", u"has_value": False}, {u"token": u"41", u"has_value": False}, {u"token": u"123", u"has_value": False}, {u"token": u"286", u"has_value": False}, {u"token": u"347", u"has_value": True, u"value": u"a"}, {u"token": u"59", u"has_value": False}, {u"token": u"347", u"has_value": True, u"value": u"a"}, {u"token": u"61", u"has_value": False}, {u"token": u"346", u"has_value": True, u"value": u"0"}, {u"token": u"59", u"has_value": False}, {u"token": u"284", u"has_value": False}, {u"token": u"40", u"has_value": False}, {u"token": u"347", u"has_value": True, u"value": u"a"}, {u"token": u"325", u"has_value": False}, {u"token": u"346", u"has_value": True, u"value": u"0"}, {u"token": u"41", u"has_value": False}, {u"token": u"123", u"has_value": False}, {u"token": u"286", u"has_value": False}, {u"token": u"347", u"has_value": True, u"value": u"b"}, {u"token": u"61", u"has_value": False}, {u"token": u"346", u"has_value": True, u"value": u"1"}, {u"token": u"47", u"has_value": False}, {u"token": u"347", u"has_value": True, u"value": u"a"}, {u"token": u"59", u"has_value": False}, {u"token": u"347", u"has_value": True, u"value": u"cout"}, {u"token": u"323", u"has_value": False}, {u"token": u"347", u"has_value": True, u"value": u"b"}, {u"token": u"323", u"has_value": False}, {u"token": u"347", u"has_value": True, u"value": u"endl"}, {u"token": u"59", u"has_value": False}, {u"token": u"125", u"has_value": False}, {u"token": u"297", u"has_value": False}, {u"token": u"346", u"has_value": True, u"value": u"0"}, {u"token": u"59", u"has_value": False}, {u"token": u"125", u"has_value": False}]

    def getTokens2(self):
        return [{u"token": u"315", u"has_value": False}, {u"token": u"289", u"has_value": False}, {u"token": u"347", u"has_value": True, u"value": u"std"}, {u"token": u"59", u"has_value": False}, {u"token": u"286", u"has_value": False}, {u"token": u"347", u"has_value": True, u"value": u"main"}, {u"token": u"40", u"has_value": False}, {u"token": u"317", u"has_value": False}, {u"token": u"41", u"has_value": False}, {u"token": u"123", u"has_value": False}, {u"token": u"286", u"has_value": False}, {u"token": u"347", u"has_value": True, u"value": u"a"}, {u"token": u"59", u"has_value": False}, {u"token": u"347", u"has_value": True, u"value": u"a"}, {u"token": u"61", u"has_value": False}, {u"token": u"346", u"has_value": True, u"value": u"0"}, {u"token": u"59", u"has_value": False}, {u"token": u"284", u"has_value": False}, {u"token": u"40", u"has_value": False}, {u"token": u"347", u"has_value": True, u"value": u"a"}, {u"token": u"326", u"has_value": False}, {u"token": u"346", u"has_value": True, u"value": u"0"}, {u"token": u"41", u"has_value": False}, {u"token": u"123", u"has_value": False}, {u"token": u"286", u"has_value": False}, {u"token": u"347", u"has_value": True, u"value": u"b"}, {u"token": u"61", u"has_value": False}, {u"token": u"346", u"has_value": True, u"value": u"1"}, {u"token": u"47", u"has_value": False}, {u"token": u"347", u"has_value": True, u"value": u"a"}, {u"token": u"59", u"has_value": False}, {u"token": u"347", u"has_value": True, u"value": u"cout"}, {u"token": u"323", u"has_value": False}, {u"token": u"347", u"has_value": True, u"value": u"b"}, {u"token": u"323", u"has_value": False}, {u"token": u"347", u"has_value": True, u"value": u"endl"}, {u"token": u"59", u"has_value": False}, {u"token": u"125", u"has_value": False}, {u"token": u"297", u"has_value": False}, {u"token": u"346", u"has_value": True, u"value": u"0"}, {u"token": u"59", u"has_value": False}, {u"token": u"125", u"has_value": False}]

    def testEmpty(self):
        data = CxxLexer().tokenize('')
        self.assertEqual(0, len(data))
    
    def testSampleCode1(self):
        self.maxDiff = None
        code = self.getFile1()
        data = CxxLexer().tokenize(code)
        expectedOutput = self.getTokens1()
        self.assertSequenceEqual(expectedOutput, data)
    
    def testSampleCode2(self):
        self.maxDiff = None
        code = self.getFile2()
        data = CxxLexer().tokenize(code)
        expectedOutput = self.getTokens2()
        self.assertSequenceEqual(expectedOutput, data)
    
    

if __name__ == '__main__':
    unittest.main()