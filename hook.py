from config import config
from coder import Coder
from checkers import Checkers
from dictionary import Dictionary
from extractCode import CodeExtractor
from gitprovider import GitProvider
from ccdatabase import CCDatabase
from cfdatabase import CFDatabase
from codechecker import CodeChecker
from entities import *
import globals
import sys
import os
import shutil

from tensorflow.keras.models import load_model
import tensorflow.keras

import numpy as np

class Verifier():
    def __init__(self):
        self.vcs = GitProvider(config.getRepoDir())
        self.ccdb = CCDatabase(config.getCcDbFile())
        self.codeChecker = CodeChecker(config.getRepoDir())
        self.checkers = Checkers()

    def convertFilePathToRepoRelativePath(self, path):
        return os.path.relpath(path, config.getRepoDir())

    def getDiffResolvedIds(self):
        resolved = self.codeChecker.diffResolved(config.getCcRunName(), config.getTmpDir(), self.ccdb)
        ids = []
        for bug in resolved:
            ids.append(bug['reportId'])
        return ids
    
    def getBugDataFromDiff(self, obj):
        return BugData(int(obj['location']['line']), int(obj['location']['line']), obj['location']['file_name'], obj['check_name'], 'New', obj['description'], int(obj['location']['line']), None)

    def getDiffNew(self):
        new = self.codeChecker.diffNew(config.getCcRunName(), config.getTmpDir(), self.ccdb)
        ids = []
        for bug in new:
            ids.append(self.getBugDataFromDiff(bug))
        return ids
    
    def isBugDataEqual(self, b1, b2):
        if b1.getLine() != b2.getLine():
            return False
        if b1.getChecker() != b2.getChecker():
            return False
        if b1.getMessage() != b2.getMessage():
            return False
        if b1.getFile() != b2.getFile():
            return False
        if b1.getStatus() != b2.getStatus():
            return False
        if b1.getReviewStatus() != b2.getReviewStatus():
            return False
        return True
    
    def displaySuggestions(self, suggestions):
        statuses = ['Negative', 'Positive', 'Skipped']
        for s in suggestions:
            print("File: {2}, L{0}, Type: {1}".format(s.bug.getLine(), s.bug.getChecker(), s.file))
            print("Verification status: {0}".format(statuses[s.verificationStatus]))
            if s.verificationStatus in [1, 2]:
                print("Code fragment with bug: \n{0}".format(s.bugCode))
                print("Suggested code fragment for replacement: \n{0}".format(s.fixCode))
    
    def applyValidFixes(self, suggestions, files):
        for f in files:
            bugs = []
            for s in suggestions:
                if s.file == f and s.verificationStatus in [1, 2]:
                    bugs.append(s)
            bugs.sort(key=lambda x: x.bug.getLine(), reverse=True)
            for b in bugs:
                print("File: {2}, L{0}, Type: {1}... ".format(b.bug.getLine(), b.bug.getChecker(), s.file), end='')
                self.applyFix(b)
                print("Applied")
            self.vcs.applyChangeForFile(f)
    
    def applyFix(self, s):
        extractor = CodeExtractor(s.bug)
        extractor.loadCodeFromFile()
        extractor.extractBugCode()
        extractor.applyFix(s.fixCode)
        extractor.saveToFile(s.bug.getFile())
    
    def main(self):
        # Do analysis
        shutil.rmtree(config.getTmpDir())
        self.codeChecker.check(True)

        # Diff new
        newBugs = self.getDiffNew()

        if len(newBugs) < 1:
            print('No new bugs introduced, commit is accepted!')
            return
        
        print("New bugs found! Count: {0}. Attempting repairs...".format(len(newBugs)))

        # Load models
        models = {}
        for checker in globals.availableCheckers:
            models[checker] = load_model(config.cfModelFilenameFormat.format(checker))

        # Load all content from files having new
        files = set([self.convertFilePathToRepoRelativePath(x.getFile()) for x in newBugs])
        fileContents = {}
        for f in files:
            fn = config.getRepoDir() + f
            with open(fn, 'r') as fh:
                fileContents[f] = ''.join(fh.readlines())

        # For each file sort by bug line desc
        suggestions = []
        validSuggestions = 0
        for f in files:
            bugs = [x for x in newBugs if self.convertFilePathToRepoRelativePath(x.getFile()) == f]
            bugs.sort(key=lambda x: x.getLine(), reverse=True)
            print("=== File: {0} ===".format(f))
            # For each bug get a suggestion and test it
            for b in bugs:
                print("L{0}, Type: {1}".format(b.getLine(), b.getChecker()))
                # Prepare useful data
                dictionary = Dictionary(b.getChecker())
                coder = Coder(dictionary)
                totalDictionaryLength = dictionary.length()
                # Prepare and extract bug fragment
                checkerInfo = self.checkers.extractTokensForChecker(b.getChecker(), b.getMessage())
                extractor = CodeExtractor(b)
                extractor.loadCodeFromText(fileContents[f])
                extractor.extractBugCode()
                bugCodeFragment = extractor.getBugCodeFragment()
                fixCodeFragment = ''
                # Encode it
                encodedBugData, initialUnkList = coder.encode(bugCodeFragment, checkerData = checkerInfo)
                # Convert to one-hot
                MODEL_X_MAX_LEN = models[b.getChecker()].get_layer(index = 0).input_shape[1]

                if len(encodedBugData) > MODEL_X_MAX_LEN:
                    print("Ignored: Code too big for model")
                    continue

                noZerosToPad = MODEL_X_MAX_LEN - len(encodedBugData)
                if noZerosToPad > 0:
                    encodedBugData = coder.applyPadding(encodedBugData, noZerosToPad)
                X = np.zeros((1, MODEL_X_MAX_LEN, totalDictionaryLength))
                X[0] = coder.convertToOneHot(encodedBugData, np.zeros((MODEL_X_MAX_LEN, totalDictionaryLength)))
                # Predict and convert from one-hot
                Y = coder.convertFromOneHot(models[b.getChecker()].predict(X)[0])
                Y = coder.removePadding(Y)
                # Decode
                fixCodeFragment = coder.decode(Y, initialUnkList)[:-1]
                
                #Verify?
                vStatus = 2
                if config.cfVerifyPrediction:
                    # Apply fix in source code file
                    extractor.applyFix(fixCodeFragment)
                    extractor.saveToFile(b.getFile())
                    # Run CodeChecker and analyze code
                    shutil.rmtree(config.getTmpDir())
                    compilationLog = self.codeChecker.check(True)
                    newBugsAfterFix = self.getDiffNew()
                    # Check if ID is resolved in tmp folder
                    isFixed = 'Build failed' not in compilationLog
                    for nb in newBugsAfterFix:
                        if self.isBugDataEqual(b, nb):
                            isFixed = False
                    # Set vStatus accordingly
                    if isFixed:
                        vStatus = 1
                    else:
                        vStatus = 0
                    # Revert file
                    extractor.loadCodeFromText(fileContents[f])
                    extractor.saveToFile(b.getFile())
                if vStatus == 0:
                    print("Verification: Negative, cannot be applied")
                elif vStatus == 1:
                    print("Verification: Positive, can be applied")
                    validSuggestions += 1
                elif vStatus == 2:
                    print("Verification: Skipped")
                    validSuggestions += 1
                sugg = SuggestionData(f, b, bugCodeFragment, fixCodeFragment, vStatus)
                suggestions.append(sugg)
        print("Valid suggestions prepared for {0} / {1} bugs.".format(validSuggestions, len(newBugs)))

        if validSuggestions > 0:
            print("Apply valid suggestions (a), display them (d), ignore them (i) or abort commit (q)?")
            apply = False
            choice = True
            while choice:
                c = sys.stdin.read(1)
                if c == 'a':
                    apply = True
                    choice = False
                    print("Applying fixes...")
                elif c == 'i':
                    choice = False
                    print("Fixes ignored...")
                elif c == 'd':
                    self.displaySuggestions(suggestions)
                    print("Apply valid suggestions (a), ignore them (i) or abort commit (q)?")
                elif c == 'q':
                    print("Aborting commit...")
                    sys.exit(1)
            if apply:
                self.applyValidFixes(suggestions, files)
                print("Fixes applied!")
        if validSuggestions != len(newBugs):
            print("Unable to fix all bugs, continue with commit (c) or abort (q)?")
            choice = True
            while choice:
                c = sys.stdin.read(1)
                if c == 'c':
                    choice = False
                    print("Continuing...")
                elif c == 'q':
                    print("Aborting commit...")
                    sys.exit(1)
        else:
            print("Bugs corrected, commit is good to go!")

verify = Verifier()
verify.main()