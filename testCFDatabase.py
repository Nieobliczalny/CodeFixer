import unittest
import sqlite3
from pathlib import Path

from cfdatabase import CFDatabase
from config import config

class TestCFDatabase(unittest.TestCase):
    def testDatabaseOpenCreateSuccess(self):
        dbPath = config.getRepoDir() + "/testtmp.sqlite"
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
        dbPath = config.getRepoDir() + "/test.sqlite"
        db = CFDatabase(dbPath)
        self.assertGreater(len(db.getAllFixData()), 0)
        del db

    def testDatabaseStoreAndClean(self):
        dbPath = config.getRepoDir() + "/testtmp.sqlite"
        dbFile = Path(dbPath)
        db = CFDatabase(dbPath)
        self.assertEqual(len(db.getAllFixData()), 0)
        db.store('', '', 'a')
        self.assertEqual(len(db.getAllFixData()), 1)
        self.assertEqual(len(db.getFixDataForChecker('a')), 1)
        self.assertEqual(len(db.getFixDataForChecker('b')), 0)
        db.clean()
        self.assertEqual(len(db.getAllFixData()), 0)
        del db
        dbFile.unlink()

if __name__ == '__main__':
    unittest.main()