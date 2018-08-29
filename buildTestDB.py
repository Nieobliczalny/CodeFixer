from ccdatabase import CCDatabase
from cfdatabase import CFDatabase
from codechecker import CodeChecker
from config import config
from extractCode import CodeExtractor
from gitprovider import GitProvider
import entities
from posixdiffer import POSIXDiffer
import os
import shutil

class TestDbBuilder():
    def __init__(self):
        self.vcs = GitProvider(config.getRepoDir())
        self.ccdb = CCDatabase(config.getCcDbFile())
        self.codeChecker = CodeChecker(config.getRepoDir())
    
    def loadCommitList(self):
        self.commits = self.vcs.getAllVersions(config.getBranch())
    
    def prepareDb(self, clean = False):
        self.db = CFDatabase(config.getCfDbFile())
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
        resolved = self.codeChecker.diffResolved(config.getCcRunName(), config.getTmpDir())
        ids = []
        for bug in resolved:
            ids.append(bug['reportId'])
        return ids
    
    def convertFilePathToRepoRelativePath(self, path):
        return os.path.relpath(path, config.getRepoDir())
    
    def extractCode(self, id):
        bugData = self.ccdb.getNotResolvedBugData(id)
        #TODO: Possible improvement for bugData
        if bugData is None:
            #TODO: Implement custom errors
            return None
            
        fileRelativePath = self.convertFilePathToRepoRelativePath(bugData.getFile())
        try:
            fullCodeWithBug = self.vcs.getFileContents(fileRelativePath, self.commits[self.currentCommitIndex + 1])
            fullCodeWithoutBug = self.vcs.getFileContents(fileRelativePath, self.commits[self.currentCommitIndex])
        except KeyError as extractError:
            return None

        diff = POSIXDiffer().diff(fullCodeWithBug, fullCodeWithoutBug)

        extractor = CodeExtractor(bugData)
        try:
            extractor.extractAll(fullCodeWithBug, diff)
        except ValueError as extractError:
            return None
        
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
        shutil.rmtree(config.getTmpDir())
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
        shutil.rmtree(config.getTmpDir())
        print('done')
    
    def iterateThroughVcsHistory(self):
        while self.checkoutToNextVersion():
            self.findAndStoreFixDataForVersion()
    
    def build(self, clean = False):
        self.prepareEnv(clean)
        self.iterateThroughVcsHistory()

def main(clean = False):
    builder = TestDbBuilder()
    builder.build(clean)

if __name__ == "__main__":
    #TODO: Parametrize it
    main(True)