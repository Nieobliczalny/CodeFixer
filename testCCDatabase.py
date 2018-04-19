import unittest
import sqlite3
from pathlib import Path

from ccdatabase import CCDatabase

class TestCCDatabase(unittest.TestCase):
    def testDatabaseOpenNonExistingFailure(self):
        dbPath = "./testdata/testtmp.sqlite"
        with self.assertRaises(FileNotFoundError):
            db = CCDatabase(dbPath)

    def testDatabaseOpenExistingSuccess(self):
        dbPath = "/home/Krystian/.codechecker/Default.sqlite"
        db = CCDatabase(dbPath)
        self.assertGreater(len(db.getAllReports()), 0)

if __name__ == '__main__':
    unittest.main()