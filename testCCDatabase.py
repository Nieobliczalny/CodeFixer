import unittest
import sqlite3
from pathlib import Path

import ccdatabase

class TestCCDatabase(unittest.TestCase):
    def testDatabaseOpenNonExistingFailure(self):
        dbPath = "./testdata/testtmp.sqlite"
        with self.assertRaises(FileNotFoundError):
            conn = ccdatabase.connect(dbPath)

    def testDatabaseOpenExistingSuccess(self):
        dbPath = "/home/Krystian/.codechecker/Default.sqlite"
        conn = ccdatabase.connect(dbPath)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM reports")
        self.assertGreater(len(cursor.fetchall()), 0)
        conn.close()

if __name__ == '__main__':
    unittest.main()