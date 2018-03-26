import config

class VCSProvider():
    def getAllVersions(self, tag):
        raise NotImplementedError
    def checkout(self, version):
        raise NotImplementedError
    def getFileContents(self, file, version):
        raise NotImplementedError
    def createBranch(self, name, version):
        raise NotImplementedError
    def createChange(self):
        raise NotImplementedError
    def applyChange(self, change):
        raise NotImplementedError