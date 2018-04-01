import unittest

import gitprovider
import config

class TestGitProvider(unittest.TestCase):
    def testLoadRootCommit(self):
        gp = gitprovider.GitProvider(config.test_repo)
        commits = gp.getAllVersions('master')
        self.assertEqual('e46f62cbdcd7447dc6c796d917fece54426c782f', commits[-1])

if __name__ == '__main__':
    unittest.main()