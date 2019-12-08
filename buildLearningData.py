from cfdatabase import CFDatabase
from config import config
from coder import Coder
from checkers import Checkers
from dictionary import Dictionary
import globals
import sys
import json

class LearningDataBuilder():
    def __init__(self):
        self.db = CFDatabase(config.getCfDbFile())
        self.checkers = Checkers()
    
    def build(self, checker):
        # Initialize coder
        print("Initializing coder...")
        self.dictionary = Dictionary(checker)
        self.coder = Coder(self.dictionary)

        # Load all data from DB
        print("Fetching data from database...")
        allData = self.db.getFixDataForChecker(checker)
        allDataLen = len(allData)
        print("Done, fetched {0} records".format(allDataLen))
        if allDataLen < 1:
            print("No data found")
            return
        
        # Encode all data
        print("Encoding all data and writing to output file...")
        i = 0
        (maxBug, maxFix, maxUnk) = self.checkers.getModelStatsForChecker(checker)
        with open(config.cfTrainFilenameFormat.format(checker), 'w') as f:
            while i < allDataLen:
                checkerInfo = self.checkers.extractTokensForChecker(checker, allData[i][4])
                encodedBugData, initialUnkList = self.coder.encode(allData[i][1], checkerData = checkerInfo)
                encodedFixData, finalUnkList = self.coder.encode(allData[i][2], unkList = initialUnkList, reverse = False)
                if -1 in encodedBugData:
                    print("{0}: [{2} - {3} ({1})] Some tokens were not parsed (bug), ignoring (lenUnk = {1})".format(i+1, len(finalUnkList), len(encodedBugData), len(encodedFixData)))
                elif -1 in encodedFixData:
                    print("{0}: [{2} - {3} ({1})] Some tokens were not parsed (fix), ignoring (lenUnk = {1})".format(i+1, len(finalUnkList), len(encodedBugData), len(encodedFixData)))
                elif len(encodedBugData) > maxBug or len(encodedFixData) > maxFix or len(finalUnkList) > maxUnk:
                    print("{0}: [{2} - {3} ({1})] Some tokens were not parsed (lengths), ignoring (lenUnk = {1})".format(i+1, len(finalUnkList), len(encodedBugData), len(encodedFixData)))
                else:
                    print("{0}: [{2} - {3} ({1})] Done (lenUnk = {1})".format(i+1, len(finalUnkList), len(encodedBugData), len(encodedFixData)))
                    f.write(json.dumps({'x': encodedBugData, 'y': encodedFixData}) + '\n')

                i += 1
                print('Done {0}'.format(i), file=sys.stderr)
        
        print("All done, exiting...")
    
def main(checker):
    builder = LearningDataBuilder()
    builder.build(checker)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("No checker name given, exiting...")
    elif sys.argv[1] not in globals.availableCheckers:
        print("No handler found for specified checker, exiting...")
    else:
        main(sys.argv[1])