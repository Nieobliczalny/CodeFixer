from cfdatabase import CFDatabase
from config import config
from coder import Coder
from checkers import Checkers
from dictionary import Dictionary
import globals
import sys
import json

import unittest

class TestCoder(unittest.TestCase):
    def setUp(self):
        # Init coder
        print("Initializing coder...")
        self.checker = self.checkerList[self.checkerIndex]
        self.dictionary = Dictionary(self.checker)
        self.coder = Coder(self.dictionary)
        # Load all data from DB
        print("Fetching data from database...")
        self.allData = self.db.getFixDataForChecker(self.checker)
        self.allDataLen = len(self.allData)
        print("Done, fetched {0} records".format(self.allDataLen))

    def tearDown(self):
        self.checkerIndex += 1

    @classmethod
    def setUpClass(self):
        print("Starting up...")
        self.db = CFDatabase(config.getCfDbFile())
        self.checkers = Checkers()
        self.checkerList = ['deadcode.DeadStores']
        self.checkerIndex = 0
    
    def testDeadcodeDeadStores(self):
        self.assertTrue(self.allDataLen > 0, msg="No data found")
        
        # Encode all data
        print("Testing encoding")
        i = 0
        while i < self.allDataLen:
            checkerInfo = self.checkers.extractTokensForChecker(self.checker, self.allData[i][4])
            encodedBugData, initialUnkList = self.coder.encode(self.allData[i][1], checkerData = checkerInfo)
            encodedFixData, finalUnkList = self.coder.encode(self.allData[i][2], unkList = initialUnkList, reverse = False)
            if -1 in encodedBugData:
                print("{0}: [{2} - {3} ({1})] Some tokens were not parsed (bug), ignoring (lenUnk = {1})".format(i+1, len(finalUnkList), len(encodedBugData), len(encodedFixData)))
            elif -1 in encodedFixData:
                print("{0}: [{2} - {3} ({1})] Some tokens were not parsed (fix), ignoring (lenUnk = {1})".format(i+1, len(finalUnkList), len(encodedBugData), len(encodedFixData)))
            else:
                print("{0}: [{2} - {3} ({1})] Done (lenUnk = {1})".format(i+1, len(finalUnkList), len(encodedBugData), len(encodedFixData)))
                textBug = self.coder.decode(encodedBugData, finalUnkList, True)
                textFix = self.coder.decode(encodedFixData, finalUnkList)
                self.assertEqual(textBug, self.allData[i][1])
                self.assertEqual(textFix, self.allData[i][2])
            i += 1
        
        print("All done.")

if __name__ == '__main__':
    unittest.main()