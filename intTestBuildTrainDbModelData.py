import unittest

import buildTestDB
from modelDataBuilder import ModelDataBuilder
from cfdatabase import CFDatabase
from config import config

class TestBuildTrainDBModelData(unittest.TestCase):
    def testBuildTrainDbModelData(self):
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
        modelBuilder = ModelDataBuilder()
        bugVector = modelBuilder.getEncodedBugData('core.DivideZero')
        dictionary = modelBuilder.getDictionary()
        fixVector = modelBuilder.getEncodedFixData('core.DivideZero', dictionary)
        self.assertSequenceEqual(bugVector, [[1, 2, 3, 4, 5, 6, 1, 7, 3, 8, 9, 10, 11, 2, 12, 13, 1, 4, 14, 15, 11, 15, 16, 4, 17, 18, 3, 4]])
        self.assertSequenceEqual(fixVector, [[1, 2, 3, 4, 5, 6, 1, 19, 3, 8, 9, 10, 11, 2, 12, 13, 1, 4, 14, 15, 11, 15, 16, 4, 17, 18, 3, 4]])

if __name__ == '__main__':
    unittest.main()