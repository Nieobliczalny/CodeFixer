import unittest

from diff import Diff
from diffparser import DiffParser
import config

class TestDiffParser(unittest.TestCase):
    def testDiffAdd(self):
        diffText = """8a8
> abc"""
        diffs = DiffParser().getDiffs(diffText)
        self.assertEqual(1, len(diffs))
        self.assertEqual(1, len(diffs[0].getAppends()))
        self.assertEqual('> abc', diffs[0].getAppends()[0])
        self.assertEqual(0, len(diffs[0].getDeletes()))
        self.assertEqual(DiffParser.OP_TYPE_APPEND, diffs[0].getOpType())
        self.assertEqual(8, diffs[0].getStartLineNo())
        self.assertEqual('8a8', diffs[0].getHeader())
    
    def testDiffRemove(self):
        diffText = """6d5
< abc"""
        diffs = DiffParser().getDiffs(diffText)
        self.assertEqual(1, len(diffs))
        self.assertEqual(0, len(diffs[0].getAppends()))
        self.assertEqual(1, len(diffs[0].getDeletes()))
        self.assertEqual('< abc', diffs[0].getDeletes()[0])
        self.assertEqual(DiffParser.OP_TYPE_DELETE, diffs[0].getOpType())
        self.assertEqual(6, diffs[0].getStartLineNo())
        self.assertEqual('6d5', diffs[0].getHeader())
    
    def testDiffChange(self):
        diffText = """6c6
< abcd
---
> abc"""
        diffs = DiffParser().getDiffs(diffText)
        self.assertEqual(1, len(diffs))
        self.assertEqual(1, len(diffs[0].getAppends()))
        self.assertEqual(1, len(diffs[0].getDeletes()))
        self.assertEqual('> abc', diffs[0].getAppends()[0])
        self.assertEqual('< abcd', diffs[0].getDeletes()[0])
        self.assertEqual(DiffParser.OP_TYPE_CHANGE, diffs[0].getOpType())
        self.assertEqual(6, diffs[0].getStartLineNo())
        self.assertEqual('6c6', diffs[0].getHeader())
    
    def testDiffMultiple(self):
        diffText = """6c6
< abcd
---
> abc
10c10
< dcba
---
> cba"""
        diffs = DiffParser().getDiffs(diffText)
        self.assertEqual(2, len(diffs))
        self.assertEqual(1, len(diffs[0].getAppends()))
        self.assertEqual(1, len(diffs[0].getDeletes()))
        self.assertEqual(1, len(diffs[1].getAppends()))
        self.assertEqual(1, len(diffs[1].getDeletes()))
        self.assertEqual('> abc', diffs[0].getAppends()[0])
        self.assertEqual('< abcd', diffs[0].getDeletes()[0])
        self.assertEqual('> cba', diffs[1].getAppends()[0])
        self.assertEqual('< dcba', diffs[1].getDeletes()[0])
        self.assertEqual(DiffParser.OP_TYPE_CHANGE, diffs[0].getOpType())
        self.assertEqual(DiffParser.OP_TYPE_CHANGE, diffs[1].getOpType())
        self.assertEqual(6, diffs[0].getStartLineNo())
        self.assertEqual(10, diffs[1].getStartLineNo())
        self.assertEqual('6c6', diffs[0].getHeader())
        self.assertEqual('10c10', diffs[1].getHeader())
    
    def testDiffMultiline(self):
        diffText = """8a10
> abc
> def"""
        diffs = DiffParser().getDiffs(diffText)
        self.assertEqual(1, len(diffs))
        self.assertEqual(2, len(diffs[0].getAppends()))
        self.assertEqual('> abc', diffs[0].getAppends()[0])
        self.assertEqual('> def', diffs[0].getAppends()[1])
        self.assertEqual(0, len(diffs[0].getDeletes()))
        self.assertEqual(DiffParser.OP_TYPE_APPEND, diffs[0].getOpType())
        self.assertEqual(8, diffs[0].getStartLineNo())
        self.assertEqual('8a10', diffs[0].getHeader())
    
    def testDiffAll(self):
        diffText = """6c6
< abcd
< efgh
---
> abc
> def
10d8
< dcba
< cba
12a14
> dcba
> cba"""
        diffs = DiffParser().getDiffs(diffText)
        self.assertEqual(3, len(diffs))
        self.assertEqual(2, len(diffs[0].getAppends()))
        self.assertEqual(2, len(diffs[0].getDeletes()))
        self.assertEqual(0, len(diffs[1].getAppends()))
        self.assertEqual(2, len(diffs[1].getDeletes()))
        self.assertEqual(2, len(diffs[2].getAppends()))
        self.assertEqual(0, len(diffs[2].getDeletes()))
        self.assertEqual('> abc', diffs[0].getAppends()[0])
        self.assertEqual('> def', diffs[0].getAppends()[1])
        self.assertEqual('< abcd', diffs[0].getDeletes()[0])
        self.assertEqual('< efgh', diffs[0].getDeletes()[1])
        self.assertEqual('< dcba', diffs[1].getDeletes()[0])
        self.assertEqual('< cba', diffs[1].getDeletes()[1])
        self.assertEqual('> dcba', diffs[2].getAppends()[0])
        self.assertEqual('> cba', diffs[2].getAppends()[1])
        self.assertEqual(DiffParser.OP_TYPE_CHANGE, diffs[0].getOpType())
        self.assertEqual(DiffParser.OP_TYPE_DELETE, diffs[1].getOpType())
        self.assertEqual(DiffParser.OP_TYPE_APPEND, diffs[2].getOpType())
        self.assertEqual(6, diffs[0].getStartLineNo())
        self.assertEqual(10, diffs[1].getStartLineNo())
        self.assertEqual(12, diffs[2].getStartLineNo())
        self.assertEqual('6c6', diffs[0].getHeader())
        self.assertEqual('10d8', diffs[1].getHeader())
        self.assertEqual('12a14', diffs[2].getHeader())
    
    def testDiffFailBrokenChange(self):
        diffText = """6c6
< abcd
< efgh
> abc
> def"""
        with self.assertRaises(ValueError):
            diffs = DiffParser().getDiffs(diffText)
    
    def testDiffFailBrokenAdd(self):
        diffText = """6a8
< abcd
< efgh"""
        with self.assertRaises(ValueError):
            diffs = DiffParser().getDiffs(diffText)
    
    def testDiffFailBrokenDelete(self):
        diffText = """6d4
> abc
> def"""
        with self.assertRaises(ValueError):
            diffs = DiffParser().getDiffs(diffText)
    
    def testDiffFailBrokenHeader(self):
        diffText = """6x4
> abc
> def"""
        with self.assertRaises(ValueError):
            diffs = DiffParser().getDiffs(diffText)

if __name__ == '__main__':
    unittest.main()