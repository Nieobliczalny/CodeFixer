class VCSProvider():
    def __init__(self, repoDir):
        raise NotImplementedError
    def getAllVersions(self, tag):
        raise NotImplementedError
    def checkout(self, version):
        raise NotImplementedError
    def getTree(self):
        raise NotImplementedError
    def getFileContents(self, file, version, charset = 'ascii'):
        raise NotImplementedError
    def createBranch(self, name, version):
        raise NotImplementedError
    def createChange(self):
        raise NotImplementedError
    def applyChange(self, change):
        raise NotImplementedError
    def applyChangeForFile(self, file):
        raise NotImplementedError