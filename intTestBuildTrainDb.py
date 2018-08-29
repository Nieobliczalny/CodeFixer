import unittest

import buildTestDB
from cfdatabase import CFDatabase
from config import config

class TestBuildTrainDB(unittest.TestCase):
    def testBuildTrainDbClean(self):
        #TODO: Start clean CC server
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

if __name__ == '__main__':
    unittest.main()