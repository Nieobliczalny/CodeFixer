import unittest
import sqlite3
from pathlib import Path

import cfdatabase

class TestCFDatabase(unittest.TestCase):
    def testDatabaseOpenSuccess(self):
        dbPath = "./testdata/test.sqlite"
        dbFile = Path(dbPath)
        if dbFile.is_file():
            dbFile.unlink()
        conn = cfdatabase.connect(dbPath)
        conn.close()
        dbFile = Path(dbPath)
        self.assertTrue(dbFile.is_file())
        conn = sqlite3.connect(dbPath)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM fix_data LIMIT 1")
        self.assertEqual(len(cursor.fetchall()), 0)
        dbFile.unlink()

if __name__ == '__main__':
    unittest.main()