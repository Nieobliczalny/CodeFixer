#Fork of https://github.com/glanois/code/blob/master/python/ppt/diff.py
#With few minor modifications

import sys, optparse
import itertools

from difflib import SequenceMatcher
from differ import Differ

class POSIXDiffer(Differ):
    """
    This class produces differences in the POSIX default format 
    (see http://www.unix.com/man-page/POSIX/1posix/diff/),
    which is the same as the Gnu diff "normal format"
    (see http://www.gnu.org/software/diffutils/manual/diffutils.html#Normal).
    """

    def compare(self, a, b):
        cruncher = SequenceMatcher(self.linejunk, a, b)
        for tag, alo, ahi, blo, bhi in cruncher.get_opcodes():
            if alo == ahi:
                f1 = '%d' % alo
            elif alo+1 == ahi:
                f1 = '%d' % (alo+1)
            else:
                f1 = '%d,%d' % (alo+1, ahi)

            if blo == bhi:
                f2 = '%d' % blo
            elif blo+1 == bhi:
                f2 = '%d' % (blo+1)
            else:
                f2 = '%d,%d' % (blo+1, bhi)

            if tag == 'replace':
                g = itertools.chain([ '%sc%s\n' % (f1, f2) ], self._my_plain_replace(a, alo, ahi, b, blo, bhi))
            elif tag == 'delete':
                g = itertools.chain([ '%sd%s\n' % (f1, f2) ], self._dump('<', a, alo, ahi))
            elif tag == 'insert':
                g = itertools.chain([ '%sa%s\n' % (f1, f2) ], self._dump('>', b, blo, bhi))
            elif tag == 'equal':
                g = []
            else:
                raise ValueError#, 'unknown tag %r' % (tag,)

            for line in g:
                yield line

    def _my_plain_replace(self, a, alo, ahi, b, blo, bhi):
        assert alo < ahi and blo < bhi
        first  = self._dump('<', a, alo, ahi)
        second = self._dump('>', b, blo, bhi)

        for g in first, '---\n', second:
            for line in g:
                yield line
    
    def splitLinesWithRetainingLineFeed(self, text):
        lines = text.split('\n')
        for i in range(len(lines)):
            lines[i] = lines[i] + '\n'
        return lines

    def diff(self, a, b):
        """
        Compare `a` and `b` (lists of strings); return a POSIX/Gnu "normal format" diff.
        """
        a = self.splitLinesWithRetainingLineFeed(a)
        b = self.splitLinesWithRetainingLineFeed(b)
        generator = self.compare(a, b)
        diff = []
        for line in generator:
            diff.append(line)
        diffText = ''.join(diff)
        if len(diffText) > 0 and diffText[-1] == '\n':
            diffText = diffText[:-1]
        return diffText