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
        self.ccNoOfJobs = int(configParser['CodeChecker']['noOfJobs'])
        self.ccUseNativeDiffResolved = self.toBool(configParser['CodeChecker']['useNativeDiff'], True)
        self.noOfLinesBefore = int(configParser['CodeFixer']['linesBeforeBug'])
        self.noOfLinesAfter = int(configParser['CodeFixer']['linesAfterBug'])
        self.cfDbFile = configParser['CodeFixer']['dbFile']
        self.cfLabelThreshold = int(configParser['CodeFixer']['labelThreshold'])
        self.cfNoOfUnkTokens = int(configParser['CodeFixer']['noOfUnkTokens'])
        self.cfDictFilenameFormat = configParser['CodeFixer']['dictFilenameFormat']
        self.cfTrainFilenameFormat = configParser['CodeFixer']['trainFilenameFormat']
        self.cfModelFilenameFormat = configParser['CodeFixer']['modelFilenameFormat']
        self.cfTrainNoEpochs = int(configParser['CodeFixer']['trainNoEpochs'])
        self.cfTrainBatchSize = int(configParser['CodeFixer']['trainBatchSize'])
        self.cfTrainHiddenSize = int(configParser['CodeFixer']['trainHiddenSize'])
        self.cfTrainNumLayers = int(configParser['CodeFixer']['trainNumLayers'])
        self.cfVerifyPrediction = self.toBool(configParser['CodeFixer']['verifyPrediction'], False)
        self.repoDir = configParser['Repository']['path']
        self.repoBranch = configParser['Repository']['branch']
        self.tmpDir = configParser['Other']['tmpDir']
    
    def toBool(self, value, defaultValue):
        if value == 'true':
            return True
        elif value == 'false':
            return False
        else:
            return defaultValue
    
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
    
    def getCcNoOfJobs(self):
        return self.ccNoOfJobs
    
    def getNoOfLinesBefore(self):
        return self.noOfLinesBefore
    
    def getNoOfLinesAfter(self):
        return self.noOfLinesAfter
    
    def getCfDbFile(self):
        return self.cfDbFile
    
    def getCfLabelThreshold(self):
        return self.cfLabelThreshold
        
    def getCfNoOfUnkTokens(self):
        return self.cfNoOfUnkTokens
        
    def getCfDictFilenameFormat(self):
        return self.cfDictFilenameFormat
        
    def getCfTrainFilenameFormat(self):
        return self.cfTrainFilenameFormat
        
    def getCfModelFilenameFormat(self):
        return self.cfModelFilenameFormat
        
    def getCfVerifyPrediction(self):
        return self.cfVerifyPrediction
    
    def getRepoDir(self):
        return self.repoDir
    
    def getBranch(self):
        return self.repoBranch
    
    def getTmpDir(self):
        return self.tmpDir

    def setBranch(self, branchName):
        self.repoBranch = branchName

config = Config()