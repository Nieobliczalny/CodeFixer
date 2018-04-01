import config
import vcsprovider

from git import Repo

#TODO: Create constructor and field for repo
class GitProvider(vcsprovider.VCSProvider):
    def getAllVersions(self, tag):
        repo = Repo(config.repo)
        versions = list(repo.iter_commits(tag))
        hashes = [x.hexsha for x in versions]
        return hashes