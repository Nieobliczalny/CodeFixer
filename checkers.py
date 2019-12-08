import re

class Checkers():
    def extractTokensForChecker(self, checkerName, message):
        if checkerName == 'deadcode.DeadStores':
            return self.extractTokenDeadStores(message)
        #TODO: Custom errors
        raise ValueError
    def extractTokenDeadStores(self, message):
        # Value stored to '<TOKEN_1>' is never read
        #define T_ID 347
        pattern = "'(.+)'"  
        varName = re.search(pattern, message).group(0)[1:-1]
        return [{'token': 347, 'has_value': True, 'value': varName}]
    def getModelStatsForChecker(self, checkerName):
        if checkerName == 'deadcode.DeadStores':
            return self.getModelStatsDeadStores()
        #TODO: Custom errors
        raise ValueError
    def getModelStatsDeadStores(self):
        return (75, 75, 10)