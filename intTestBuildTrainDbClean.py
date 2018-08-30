import unittest

import buildTestDB
from cfdatabase import CFDatabase
from config import config

class TestBuildTrainDBClean(unittest.TestCase):
    def testBuildTrainDbClean(self):
        dbPath = config.getCfDbFile()
        db = CFDatabase(dbPath)
        db.clean()
        self.assertEqual(len(db.getAllFixData()), 0)
        del db
        buildTestDB.main(True)
        db = CFDatabase(dbPath)
        self.assertEqual(len(db.getAllFixData()), 2)
        self.assertEqual(db.getAllFixData()[0][3], 'deadcode.DeadStores')
        self.assertEqual(db.getAllFixData()[1][3], 'core.DivideZero')
        self.assertEqual(db.getLastCommit(), 'f2917b938f0ecbc62ad48101d034369a1ae61a19')

if __name__ == '__main__':
    unittest.main()