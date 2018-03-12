import database
import config

def extractBugCode(bugData):
    file = open(bugData[4], 'r')
    lines = file.readlines()
    linesCount = len(lines)
    file.close()
    #-1 because we have 1st line at index 0
    startLine = bugData[0] - config.noOfLinesBefore - 1
    if startLine < 0:
        startLine = 0
    #we dont subtract 1 case we want to include last line also (endLine is excluded)
    endLine = bugData[2] + config.noOfLinesAfter
    if endLine > linesCount:
        endLine = linesCount
    if startLine >= bugData[0] or endLine < bugData[2]:
        #TODO: Implement custom errors
        raise ValueError
    return ''.join(lines[startLine:endLine])

conn = database.connect(config.dbFile)
bugs = database.getAllBugs(conn)
for bug in bugs:
    print(bug)
    data = database.getBugData(conn, bug[0])
    print(data)
    print(extractBugCode(data))
conn.close()