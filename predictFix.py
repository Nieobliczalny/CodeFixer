from config import config
from coder import Coder
from checkers import Checkers
from dictionary import Dictionary
from extractCode import CodeExtractor
from gitprovider import GitProvider
from ccdatabase import CCDatabase
from cfdatabase import CFDatabase
from codechecker import CodeChecker
import globals
import sys
import os

from tensorflow.keras.models import load_model
import tensorflow.keras

import numpy as np

class Predictor():
    def __init__(self):
        self.vcs = GitProvider(config.getRepoDir())
        self.ccdb = CCDatabase(config.getCcDbFile())
        self.codeChecker = CodeChecker(config.getRepoDir())
        self.checkers = Checkers()
        self.loadCommitList()
    
    def loadCommitList(self):
        self.commits = self.vcs.getAllVersions(config.getBranch())
        self.currentCommitIndex = 0
    
    def convertFilePathToRepoRelativePath(self, path):
        return os.path.relpath(path, config.getRepoDir())
    
    def getDiffResolvedIds(self):
        resolved = self.codeChecker.diffResolved(config.getCcRunName(), config.getTmpDir(), self.ccdb)
        ids = []
        for bug in resolved:
            ids.append(bug['reportId'])
        return ids
    
    def predict(self, id, checker):
        # Load all bugs
        print("Loading bug data...")
        ids = []
        if id == -1:
            bugs = self.ccdb.getAllBugsForChecker(checker)
            ids = [x[0] for x in bugs]
        else:
            ids.append(id)
        
        # Loading model
        print("Loading model...")
        model = load_model(config.cfModelFilenameFormat.format(checker))
        model.summary()
        vLabels = ['NOT OK', 'OK', 'Skipped']

        # Initialize coder
        print("Initializing coder...")
        self.dictionary = Dictionary(checker)
        self.coder = Coder(self.dictionary)
        self.totalDictionaryLength = self.dictionary.length()

        # Predicting
        print("Starting predictions...")
        for i in ids:
            allData = self.ccdb.getBugData(i)
            if allData.getChecker() not in globals.availableCheckers or allData.getChecker() != checker:
                print("Bug #{0} - checker not supported".format(i))
            else:
                # Load extra tokens from checker message
                checkerInfo = self.checkers.extractTokensForChecker(allData.getChecker(), allData.getMessage())
                # Retrieve code fragment with bug
                fileRelativePath = self.convertFilePathToRepoRelativePath(allData.getFile())
                fullCodeWithBug = self.vcs.getFileContents(fileRelativePath, self.commits[self.currentCommitIndex])
                extractor = CodeExtractor(allData)
                extractor.loadCodeFromText(fullCodeWithBug)
                extractor.extractBugCode()
                bugCodeFragment = extractor.getBugCodeFragment()
                fixCodeFragment = ''
                # Encode it
                encodedBugData, initialUnkList = self.coder.encode(bugCodeFragment, checkerData = checkerInfo)
                # Convert to one-hot
                MODEL_X_MAX_LEN = model.get_layer(index = 0).input_shape[1]
                if len(encodedBugData) > MODEL_X_MAX_LEN:
                    print("Bug #{0} - Code too big for model, ignored".format(i))
                    continue
                elif id == -1:
                    print("Bug #{0} - Good to go".format(i))
                    continue
                noZerosToPad = MODEL_X_MAX_LEN - len(encodedBugData)
                if noZerosToPad > 0:
                    encodedBugData = self.coder.applyPadding(encodedBugData, noZerosToPad)
                X = np.zeros((1, MODEL_X_MAX_LEN, self.totalDictionaryLength))
                X[0] = self.coder.convertToOneHot(encodedBugData, np.zeros((MODEL_X_MAX_LEN, self.totalDictionaryLength)))
                # Predict and convert from one-hot
                Y = self.coder.convertFromOneHot(model.predict(X)[0])
                print(Y)
                # Decode
                Y = self.coder.removePadding(Y)
                fixCodeFragment = self.coder.decode(Y, initialUnkList)
                
                #Verify?
                vStatus = 2
                if config.cfVerifyPrediction:
                    # Apply fix in source code file
                    extractor.applyFix(fixCodeFragment)
                    extractor.saveToFile(allData.getFile())
                    # Run CodeChecker and analyze code
                    self.codeChecker.check(True)
                    resolvedIds = self.getDiffResolvedIds()
                    # Check if ID is resolved in tmp folder
                    isFixed = i in resolvedIds
                    # Set vStatus accordingly
                    if isFixed:
                        vStatus = 1
                    else:
                        vStatus = 0
                #Print
                print("Bug #{0} - summary".format(i))
                print("== Code fragment with bug ==")
                print(bugCodeFragment)
                print("== Suggested fix ==")
                print(fixCodeFragment)
                print("Verification: {0}".format(vLabels[vStatus]))
                a = ' '
                while a != 'y' and a != 'n':
                    a = input("Apply fix? (y/n): ")
                if a == 'y':
                    if not config.cfVerifyPrediction:
                        # Apply fix in source code file
                        extractor.applyFix(fixCodeFragment)
                        extractor.saveToFile(allData.getFile())
                elif config.cfVerifyPrediction:
                    # Revert file contents
                    self.vcs.checkout(self.commits[self.currentCommitIndex])
                print('Done')
        print("All done, exiting...")
    
def main(id, checker):
    predictor = Predictor()
    predictor.predict(id, checker)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("No checker given, exiting...")
    elif len(sys.argv) < 3:
        print("No bug id given, assuming all...")
        main(-1, sys.argv[1])
    else:
        main(int(sys.argv[2]), sys.argv[1])