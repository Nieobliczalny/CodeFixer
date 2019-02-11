import unittest

import gitprovider
from config import config

class TestGitProvider(unittest.TestCase):
    def testLoadRootCommit(self):
        gp = gitprovider.GitProvider(config.getRepoDir())
        commits = gp.getAllVersions(config.getBranch())
        self.assertEqual('e46f62cbdcd7447dc6c796d917fece54426c782f', commits[-1])#'bde8d75eb1133703b93a5110ed01c635d6d886ac', commits[-1])
    
    def testCheckout(self):
        gp = gitprovider.GitProvider(config.getRepoDir())
        gp.checkout('e46f62cbdcd7447dc6c796d917fece54426c782f')#'bde8d75eb1133703b93a5110ed01c635d6d886ac')
        #self.assertEqual(3, len(gp.getTree().blobs))
        self.assertEqual(2, len(gp.getTree().blobs))
        gp.checkout('955fa1826edfc9a0936201675029492669a3ec81')#'52a7d8e413686e54d23dbf002f68f6c9baeaa313')
        #self.assertEqual(4, len(gp.getTree().blobs))
        self.assertEqual(3, len(gp.getTree().blobs))
    
    def testFileContents(self):
        gp = gitprovider.GitProvider(config.getRepoDir())
        contents = gp.getFileContents('bugcode2.cpp', 'bbe7c95cbbbe1ce8871a5e1fad674ee245e52314')#'3242a5e8d56da17553feee2b61fa424963148c82')
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
        contents = gp.getFileContents('bugcode2.cpp', 'c1b5543440eb2e671018736d79f9a8a4e96f4855')#'f9aac9d2cb840744f64ce8882fd4202884139680')
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
        gp = gitprovider.GitProvider(config.getRepoDir())
        with self.assertRaises(ValueError):
            gp.checkout('0000000000000000000000000000000000000002')
    
    def testGetFileContentsNotExistingFileFailure(self):
        gp = gitprovider.GitProvider(config.getRepoDir())
        with self.assertRaises(KeyError):
            gp.getFileContents('bugcode2.cpp', 'e46f62cbdcd7447dc6c796d917fece54426c782f')#'bde8d75eb1133703b93a5110ed01c635d6d886ac')
    
    def testGetFileContentsNotExistingCommitFailure(self):
        gp = gitprovider.GitProvider(config.getRepoDir())
        with self.assertRaises(ValueError):
            gp.getFileContents('bugcode.cpp', '0000000000000000000000000000000000000002')
    
    @classmethod
    def tearDownClass(self):
        gp = gitprovider.GitProvider(config.getRepoDir())
        gp.checkout('master')

if __name__ == '__main__':
    unittest.main()