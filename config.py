import configparser

class Config():
    def __init__(self):
        configParser = configparser.ConfigParser()
        configParser.read('config.ini')
        self.ccPath = configParser['CodeChecker']['path']
        self.ccBin = configParser['CodeChecker']['relativeBinPath']
        self.ccVenv = configParser['CodeChecker']['relativeVenv']
        self.ccDbFile = configParser['CodeChecker']['dbFile']
        self.ccRunName = configParser['CodeChecker']['runName']
        self.noOfLinesBefore = int(configParser['CodeFixer']['linesBeforeBug'])
        self.noOfLinesAfter = int(configParser['CodeFixer']['linesAfterBug'])
        self.cfDbFile = configParser['CodeFixer']['dbFile']
        self.repoDir = configParser['Repository']['path']
        self.repoBranch = configParser['Repository']['branch']
        self.tmpDir = configParser['Other']['tmpDir']
    
    def getCcDbFile(self):
        return self.ccDbFile
    
    def getCcRunName(self):
        return self.ccRunName
    
    def getCcPath(self):
        return self.ccPath
    
    def getCcRelativeBinPath(self):
        return self.ccBin
    
    def getCcRelativeVenv(self):
        return self.ccVenv
    
    def getNoOfLinesBefore(self):
        return self.noOfLinesBefore
    
    def getNoOfLinesAfter(self):
        return self.noOfLinesAfter
    
    def getCfDbFile(self):
        return self.cfDbFile
    
    def getRepoDir(self):
        return self.repoDir
    
    def getBranch(self):
        return self.repoBranch
    
    def getTmpDir(self):
        return self.tmpDir

config = Config()