from ccdatabase import CCDatabase
from cfdatabase import CFDatabase
from config import config
from cxxlexer import CxxLexer
from checkers import Checkers
import sys
from collections import deque
from itertools import groupby
import json

class DictionaryBuilder():
    def __init__(self):
        self.db = CFDatabase(config.getCfDbFile())
        self.lexer = CxxLexer()
        self.checkers = Checkers()
    
    def build(self, checker):
        # Load all data from DB
        print("Fetching data from database...")
        allData = self.db.getFixDataForChecker(checker)
        allDataLen = len(allData)
        print("Done, fetched {0} records".format(allDataLen))
        if allDataLen < 1:
            print("No data found")
            return
        
        # Tokenize all code snippets and extract extra tokens from checker's messages
        # Labelize all tokens existing only in fixed code (added data)
        # Labelize all tokens appearing more than X times
        # Labelize all C++ STL names (namespaces, constants, defines, variables, functions, headers, numeric literals)
        # Labelize all UNK token indexes
        print("Converting to tokens...")
        tokens = deque()
        tokensLen = 0
        labels = {}
        NO_VALUE_LABEL = "<NO_VALUE>"
        i = 0
        tokensLen = 0

        minTokens1Len = 9999
        minTokens2Len = 9999
        maxTokens1Len = 0
        maxTokens2Len = 0

        while i < allDataLen:
            # Tokenize
            tokens1 = self.lexer.tokenize(allData[i][1])
            tokens2 = self.lexer.tokenize(allData[i][2])
            extra = self.checkers.extractTokensForChecker(checker, allData[i][4])
            newTokens = []

            # Extract new tokens
            for token2 in tokens2:
                matchFound = False
                for token1 in tokens1:
                    if token1['token'] == token2['token'] and token1['has_value'] == token2['has_value']:
                        if token1['has_value']:
                            if token1['value'] == token2['value']:
                                matchFound = True
                        else:
                            matchFound = True
                if not matchFound:
                    newTokens.append(token2)
            tokens1Len = len(tokens1)
            tokens2Len = len(tokens2)

            # Statistics
            if tokens1Len < minTokens1Len:
                minTokens1Len = tokens1Len
            if tokens2Len < minTokens2Len:
                minTokens2Len = tokens2Len
            if tokens1Len > maxTokens1Len:
                maxTokens1Len = tokens1Len
            if tokens2Len > maxTokens2Len:
                maxTokens2Len = tokens2Len
            
            # Count occurrences of each label
            allTokens = tokens1 + tokens2 + extra
            for token in allTokens:
                value = NO_VALUE_LABEL
                if token['has_value']:
                    value = token['value']
                if value in labels:
                    labels[value] += 1
                else:
                    labels[value] = 1
                tokensLen += 1
            if len(newTokens) > 0:
                tokens.append(newTokens)
            i += 1
            print('Done {0}, processed {1} tokens ({2}/{3}/{4}/{5})'.format(i, len(allTokens), tokens1Len, tokens2Len, len(extra), len(newTokens)), file=sys.stderr)
        print("Done, converted {0} tokens".format(tokensLen))

        # Labelizing
        labelDb = []
        # UNK
        print("Adding UNK token labels")
        for i in range(config.cfNoOfUnkTokens):
            labelDb.append("{0}".format(i))
        print("Done, current label DB has {0} entries".format(len(labelDb)))

        # Common occurrences
        print("Filtering labels, selecting only those with > {0} occurrences".format(config.cfLabelThreshold))
        for key in labels.keys():
            if labels[key] > config.cfLabelThreshold:
                labelDb.append(key)
        print("Done, current label DB has {0} entries".format(len(labelDb)))

        # New tokens in fixed code
        print("Filtering labels, selecting only tokens introduced with fix")
        for entry in tokens:
            for token in entry:
                if token['has_value']:
                    labelDb.append(token['value'])
        print("Done, current label DB has {0} entries".format(len(labelDb)))

        # STL part

        # Printout
        print("Uniqueing labels")
        labelsUnique = list(set(labelDb))
        print("Done, current label DB has {0} entries".format(len(labelsUnique)))
        print("Data set info")
        print("Min no of tokens (bug): {0}".format(minTokens1Len))
        print("Min no of tokens (fix): {0}".format(minTokens2Len))
        print("Max no of tokens (bug): {0}".format(maxTokens1Len))
        print("Max no of tokens (fix): {0}".format(maxTokens2Len))
        print("Extracted labels:")
        print(labelsUnique)

        # Save to file
        print("Writing to dictionary file")
        with open(config.cfDictFilenameFormat.format(checker), "w") as f:
            f.write(json.dumps(labelsUnique))
        print("Done, exiting...")
    
def main(checker):
    builder = DictionaryBuilder()
    builder.build(checker)

if __name__ == "__main__":
    checkers = ['deadcode.DeadStores']
    if len(sys.argv) < 2:
        print("No checker name given, exiting...")
    elif sys.argv[1] not in checkers:
        print("No handler found for specified checker, exiting...")
    else:
        main(sys.argv[1])