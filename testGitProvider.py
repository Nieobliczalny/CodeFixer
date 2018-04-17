import unittest

import gitprovider
import config

class TestGitProvider(unittest.TestCase):
    def testLoadRootCommit(self):
        gp = gitprovider.GitProvider(config.test_repo)
        commits = gp.getAllVersions('master')
        self.assertEqual('e46f62cbdcd7447dc6c796d917fece54426c782f', commits[-1])
    
    def testCheckout(self):
        gp = gitprovider.GitProvider(config.test_repo)
        gp.checkout('e46f62cbdcd7447dc6c796d917fece54426c782f')
        self.assertEqual(2, len(gp.getTree().blobs))
        gp.checkout('955fa1826edfc9a0936201675029492669a3ec81')
        self.assertEqual(3, len(gp.getTree().blobs))
    
    def testFileContents(self):
        gp = gitprovider.GitProvider(config.test_repo)
        contents = gp.getFileContents('bugcode2.cpp', 'bbe7c95cbbbe1ce8871a5e1fad674ee245e52314')
        expectedContent = """#include <iostream>

using namespace std;

int main(void)
{
    int a;
    a = 3;
    a = 0;
    if (a == 0)
    {
        int b = 1 / a;
        cout << b << endl;
    }
    return 0;
}"""
        self.assertEqual(expectedContent.split('\n'), contents.split('\r\n'))
        contents = gp.getFileContents('bugcode2.cpp', 'c1b5543440eb2e671018736d79f9a8a4e96f4855')
        expectedContent = """#include <iostream>

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
        self.assertEqual(expectedContent.split('\n'), contents.split('\r\n'))
    
    def testCheckoutNonExistingCommitFailure(self):
        gp = gitprovider.GitProvider(config.test_repo)
        with self.assertRaises(ValueError):
            gp.checkout('0000000000000000000000000000000000000002')
    
    def testGetFileContentsNotExistingFileFailure(self):
        gp = gitprovider.GitProvider(config.test_repo)
        with self.assertRaises(KeyError):
            gp.getFileContents('bugcode2.cpp', 'e46f62cbdcd7447dc6c796d917fece54426c782f')
    
    def testGetFileContentsNotExistingCommitFailure(self):
        gp = gitprovider.GitProvider(config.test_repo)
        with self.assertRaises(ValueError):
            gp.getFileContents('bugcode.cpp', '0000000000000000000000000000000000000002')

if __name__ == '__main__':
    unittest.main()