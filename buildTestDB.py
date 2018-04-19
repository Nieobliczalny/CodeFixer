from ccdatabase import CCDatabase
import cfdatabase
from codechecker import CodeChecker
import config
import extractCode
from gitprovider import GitProvider
import posixdiffer

class TestDbBuilder():
    def __init__(self):
        self.vcs = GitProvider(config.train_repo)
        self.ccdb = CCDatabase(config.ccDbFile)
    
    def loadCommitList(self):
        self.commits = self.vcs.getAllVersions(config.train_branch)
    
    def prepareDb(self, clean = False):
        self.db = cfdatabase.connect(config.train_db)
        #if clean:
        #    self.db.clean()
    
    def checkoutToNextVersion(self):
        self.currentCommitIndex = self.currentCommitIndex - 1
        if (self.currentCommitIndex < 0):
            return False
        self.vcs.checkout(self.commits[self.currentCommitIndex])
        return True
    
    def getDiffResolvedIds(self):
        CodeChecker().check(True)
        resolved = CodeChecker().diffResolved(config.ccRunName, config.tmpDir)
        ids = []
        for bug in resolved:
            ids.append(bug['reportId'])
        return ids
    
    #TODO: Return bug and fix code with checker name (and bug path no!)
    def extractCode(self, id):
        bugData = self.ccdb.getAllBugs()
        bugCodeFragment = extractCode.extractBugCode(bugData)
        fullCodeWithBug = self.vcs.getFileContents(bugData[4], self.commits[self.currentCommitIndex + 1])
        fullCodeWithoutBug = self.vcs.getFileContents(bugData[4], self.commits[self.currentCommitIndex])
        diff = posixdiffer.diff(fullCodeWithBug, fullCodeWithoutBug)
        usedDiffs = []
        fixCodeFragment = extractCode.extractFixCode(bugData, bugCodeFragment, diff, usedDiffs)
        #Easy version - ignore bug if none or more than one diff used to fix
        #TODO: Possible improvement here
        if len(usedDiffs) != 1:
            return False
        return True

    def prepareEnv(self):
        self.loadCommitList()
        self.prepareDb()
        self.currentCommitIndex = len(self.commits)
        self.checkoutToNextVersion()
        CodeChecker().check(True)
        CodeChecker().store(self.commits[self.currentCommitIndex])
    
    def iterateThroughVcsHistory(self):
        while self.checkoutToNextVersion():
            ids = self.getDiffResolvedIds()
            for id in ids:
                if self.extractCode(id):
                    #cfdatabase.store()
                    pass
            CodeChecker().store(self.commits[self.currentCommitIndex])
    
    def build(self):
        self.prepareEnv()
        self.iterateThroughVcsHistory()