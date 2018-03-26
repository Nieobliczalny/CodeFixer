import config
import vcsprovider

from git import Repo

#TODO: Create constructor and field for repo
class GitProvider(vcsprovider.VCSProvider):
    def getAllVersions(self, tag):
        repo = Repo(config.repo)
        return list(repo.iter_commits(tag, max_count=50))

gp = GitProvider()
print(gp.getAllVersions('master'))