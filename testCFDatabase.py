import unittest
import sqlite3
from pathlib import Path

from cfdatabase import CFDatabase

#TODO: Add test for clean and store
class TestCFDatabase(unittest.TestCase):
    def testDatabaseOpenCreateSuccess(self):
        dbPath = "./testdata/testtmp.sqlite"
        dbFile = Path(dbPath)
        if dbFile.is_file():
            dbFile.unlink()
        db = CFDatabase(dbPath)
        dbFile = Path(dbPath)
        self.assertTrue(dbFile.is_file())
        del db
        db = CFDatabase(dbPath)
        self.assertEqual(len(db.getAllFixData()), 0)
        del db
        dbFile.unlink()

    def testDatabaseOpenExistingSuccess(self):
        dbPath = "./testdata/test.sqlite"
        db = CFDatabase(dbPath)
        self.assertGreater(len(db.getAllFixData()), 0)
        del db

if __name__ == '__main__':
    unittest.main()