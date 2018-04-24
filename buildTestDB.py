from ccdatabase import CCDatabase
from cfdatabase import CFDatabase
from codechecker import CodeChecker
import config
from extractCode import CodeExtractor
from gitprovider import GitProvider
import entities
import posixdiffer
import os
import shutil

class TestDbBuilder():
    def __init__(self):
        self.vcs = GitProvider(config.train_repo)
        self.ccdb = CCDatabase(config.train_ccDbFile)
        self.codeChecker = CodeChecker(config.train_repo)
    
    def loadCommitList(self):
        self.commits = self.vcs.getAllVersions(config.train_branch)
    
    def prepareDb(self, clean = False):
        self.db = CFDatabase(config.train_db)
        if clean:
            self.db.clean()
    
    def checkoutToNextVersion(self):
        self.currentCommitIndex = self.currentCommitIndex - 1
        if (self.currentCommitIndex < 0):
            return False
        self.vcs.checkout(self.commits[self.currentCommitIndex])
        return True
    
    def getDiffResolvedIds(self):
        self.codeChecker.check(True)
        resolved = self.codeChecker.diffResolved(config.ccRunName, config.tmpDir)
        ids = []
        for bug in resolved:
            ids.append(bug['reportId'])
        return ids
    
    def convertFilePathToRepoRelativePath(self, path):
        return os.path.relpath(path, config.train_repo)
    
    def extractCode(self, id):
        bugData = self.ccdb.getNotResolvedBugData(id)
        #TODO: Possible improvement for bugData
        if bugData is None:
            #TODO: Implement custom errors
            return None
        fileRelativePath = self.convertFilePathToRepoRelativePath(bugData.getFile())
        fullCodeWithBug = self.vcs.getFileContents(fileRelativePath, self.commits[self.currentCommitIndex + 1])
        fullCodeWithoutBug = self.vcs.getFileContents(fileRelativePath, self.commits[self.currentCommitIndex])
        diff = posixdiffer.diff(fullCodeWithBug, fullCodeWithoutBug)

        extractor = CodeExtractor(bugData)
        extractor.loadCodeFromText(fullCodeWithBug)
        extractor.extractBugCode()
        extractor.loadDiff(diff)
        extractor.extractFixCode()
        bugCodeFragment = extractor.getBugCodeFragment()
        fixCodeFragment = extractor.getFixCodeFragment()
        usedDiffs = extractor.getUsedDiffs()
        #Easy version - ignore bug if none or more than one diff used to fix
        #TODO: Possible improvement here
        if len(usedDiffs) != 1:
            return None
        return entities.FixData(bugCodeFragment, fixCodeFragment, bugData.getChecker())

    def prepareEnv(self, clean = False):
        print('Loading commit list... ', end = '')
        self.loadCommitList()
        print('done')
        print('Preparing train db... ', end = '')
        self.prepareDb(clean)
        print('done')
        print('Checking out to root... ', end = '')
        self.currentCommitIndex = len(self.commits)
        self.checkoutToNextVersion()
        print('done')
        print('Initial analysis... ', end = '')
        self.codeChecker.check(True)
        print('done')
        print('Storing initial results... ', end = '')
        self.codeChecker.store(self.commits[self.currentCommitIndex])
        print('done')
        print('Cleaning up tmp directory... ', end = '')
        shutil.rmtree(config.tmpDir)
        print('done')
    
    def findAndStoreFixDataForVersion(self):
        print('Analyzing version', self.commits[self.currentCommitIndex], '... ', end = '')
        self.codeChecker.check(True)
        print('done')
        print('Getting list of resolved bugs for version', self.commits[self.currentCommitIndex],'... ', end = '')
        ids = self.getDiffResolvedIds()
        print('done')
        for id in ids:
            print('Parsing data for bug (#', id, ')... ', sep = '', end = '')
            fixData = self.extractCode(id)
            print('done')
            if fixData is not None:
                print('Storing fixData... ', end = '')
                self.db.store(fixData.getBugCode(), fixData.getFixCode(), fixData.getChecker())
                print('done')
        print('Storing CodeChecker results for this version... ', end = '')
        self.codeChecker.store(self.commits[self.currentCommitIndex])
        print('done')
        print('Cleaning up tmp directory... ', end = '')
        shutil.rmtree(config.tmpDir)
        print('done')
    
    def iterateThroughVcsHistory(self):
        while self.checkoutToNextVersion():
            self.findAndStoreFixDataForVersion()
    
    def build(self, clean = False):
        self.prepareEnv(clean)
        self.iterateThroughVcsHistory()

builder = TestDbBuilder()
builder.build(True)