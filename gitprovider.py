import vcsprovider

from git import Repo

class GitProvider(vcsprovider.VCSProvider):
    def __init__(self, repoDir):
        self.repo = Repo(repoDir)
       
    def getAllVersions(self, tag):
        versions = list(self.repo.iter_commits(tag))
        hashes = [x.hexsha for x in versions]
        return hashes
    
    def checkout(self, version):
        self.repo.head.reference = self.repo.commit(version)
        self.repo.head.reset(index=True, working_tree=True)
    
    def getTree(self):
        return self.repo.head.commit.tree
    
    def getFileContents(self, file, version, charset = 'ascii'):
        commit = self.repo.commit(version)
        blob = commit.tree[file]
        contents = blob.data_stream.read()
        return contents.decode(charset)

    def applyChangeForFile(self, file):
        self.repo.index.add([file])