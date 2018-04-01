import vcsprovider

from git import Repo

class GitProvider(vcsprovider.VCSProvider):
    def __init__(self, repoDir):
        self.repo = Repo(repoDir)
       
    def getAllVersions(self, tag):
        versions = list(self.repo.iter_commits(tag))
        hashes = [x.hexsha for x in versions]
        return hashes