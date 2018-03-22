#Python libs
import re

#Local modules
import ccdatabase
import cfdatabase
import config

def extractBugCode(bugData):
    if bugData[0] > bugData[2]:
        #TODO: Implement custom errors
        raise ValueError
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

#Returns code after applied diff, also writes each used diff id in usedDiffs
def extractFixCode(bugData, bugCode, fileDiff, usedDiffs):
    fileDiffLines = fileDiff.split('\n')
    bugCodeLines = bugCode.split('\n')
    fixCodeLines = []
    currentDiffLine = 0
    includeFileDiffOutput = False
    bugCodeLineBegin = max([bugData[0] - config.noOfLinesBefore, 1])
    bugCodeLineEnd = bugCodeLineBegin + len(bugCodeLines) - 1
    for fileDiffLine in fileDiffLines:
        if fileDiffLine[0] == '<':
            #Remove case from [2]
            if includeFileDiffOutput:
                currentDiffLine += 1
        elif fileDiffLine[0] == '>':
            #add case from [2]
            if includeFileDiffOutput:
                fixCodeLines.append(fileDiffLine[2:])
        elif fileDiffLine[0] != '-':
            #Do nothing on ---, break between A and D
            #new diff, extract line number
            #copy lines from lastLine to currentDiffLine excluded
            #unless optype is a
            m = re.search('^([0-9]+)([acd])([0-9]+)$', fileDiffLine)
            line = int(m.group(1))
            opType = m.group(2)
            if line >= bugCodeLineBegin and line <= bugCodeLineEnd:
                #We have our diff do your job
                usedDiffs.append(fileDiffLine)
                if opType == 'a':
                    line += 1
                line -= bugCodeLineBegin
                while currentDiffLine < line:
                    fixCodeLines.append(bugCodeLines[currentDiffLine])
                    currentDiffLine += 1
                includeFileDiffOutput = True
            else:
                includeFileDiffOutput = False
    while currentDiffLine < len(bugCodeLines):
        fixCodeLines.append(bugCodeLines[currentDiffLine])
        currentDiffLine += 1
    return '\n'.join(fixCodeLines)
            

#TODO: Tests!
conn = ccdatabase.connect(config.ccDbFile)
bugs = ccdatabase.getAllBugs(conn)
conn2 = cfdatabase.connect(config.cfDbFile)
diff18 = """8d7
< 	a = 3;"""
diff19 = """10c10
< 	if (a == 0)
---
> 	if (a != 0)"""
for bug in bugs:
    print(bug)
    data = ccdatabase.getBugData(conn, bug[0])
    print(data)
    bugCode = extractBugCode(data)
    print(bugCode)
    usedDiffs = []
    if bug[0] == 18:
        fixed = extractFixCode(data, bugCode, diff18, usedDiffs)
    else:
        fixed = extractFixCode(data, bugCode, diff19, usedDiffs)
    print(fixed)
    print(usedDiffs)
conn.close()