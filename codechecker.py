from config import config

import subprocess
import sys
import json
import re

class CodeChecker():
    def __init__(self, repo = None):
        if repo is None:
            self.repo = config.getRepoDir()
        else:
            self.repo = repo
    
    def check(self, clean = False):
        if clean:
            self.clean()
        jobs = ''
        if config.ccNoOfJobs > 1:
            jobs = ' -j {0}'.format(config.ccNoOfJobs)
        checkers = '-e all'
        #if len(config.customCheckers) > 0:
        #    checkers = '-d all -e {0}'.format(' -e '.join(config.customCheckers.split(',')))
        cmd = 'CodeChecker check {0} -e all -b "cd {1} && make {0}" -o {2}'.format(jobs, self.repo, config.getTmpDir())
        return self.runCmd(cmd).decode(sys.stdout.encoding)
    
    def store(self, tag):
        cmd = 'CodeChecker store {0} -n {1} --tag {2}'.format(config.getTmpDir(), config.getCcRunName(), tag)
        self.runCmd(cmd)
    
    def diffResolved(self, baseRun, newRun, db = None):
        if config.ccUseNativeDiffResolved:
            return self.nativeDiffResolved(baseRun, newRun)
        else:
            return self.customDiffResolved(baseRun, newRun, db)
    
    def diffNew(self, baseRun, newRun, db = None):
        if True or config.ccUseNativeDiffResolved:
            return self.nativeDiffNew(baseRun, newRun)
        else:
            return self.customDiffNew(baseRun, newRun, db)
    
    def nativeDiffResolved(self, baseRun, newRun):
        cmd = 'CodeChecker cmd diff -b {0} -n {1} --resolved -o json'.format(baseRun, newRun)
        stdoutData = self.runCmd(cmd).decode(sys.stdout.encoding)
        output = self.getDataAfterInfoLog(stdoutData)
        out = []
        try:
            out = json.loads(output)
        except json.decoder.JSONDecodeError:
            pass
        return out
    
    def customDiffResolved(self, baseRun, newRun, db):
        cmd = 'CodeChecker parse --print-steps {0}'.format(newRun)
        stdoutData = self.runCmd(cmd).decode(sys.stdout.encoding)
        lines = stdoutData.split("\n")
        reportHashes = []
        for line in lines:
            if "Report hash" in line:
                m = re.search('[0-9a-fA-F]{32}', line)
                reportHashes.append(m.group(0))

        uniqueHashes = set(reportHashes)
        allBugs = db.getAllBugs()
        hashToIdDict = dict([(x[2], x[0]) for x in allBugs])
        allBugsHashes = set([x[2] for x in allBugs])
        resolved = [{'reportId': hashToIdDict[x]} for x in list(allBugsHashes - uniqueHashes)]
        return resolved
    
    def nativeDiffNew(self, baseRun, newRun):
        cmd = 'CodeChecker cmd diff -b {0} -n {1} --new -o json'.format(baseRun, newRun)
        stdoutData = self.runCmd(cmd).decode(sys.stdout.encoding)
        output = self.getDataAfterInfoLog(stdoutData)
        out = []
        try:
            out = json.loads(output)
        except json.decoder.JSONDecodeError:
            pass
        return out
    
    def customDiffNew(self, baseRun, newRun, db):
        cmd = 'CodeChecker parse --print-steps {0}'.format(newRun)
        stdoutData = self.runCmd(cmd).decode(sys.stdout.encoding)
        lines = stdoutData.split("\n")
        reportHashes = []
        for line in lines:
            if "Report hash" in line:
                m = re.search('[0-9a-fA-F]{32}', line)
                reportHashes.append(m.group(0))

        uniqueHashes = set(reportHashes)
        allBugs = db.getAllBugs()
        hashToIdDict = dict([(x[2], x[0]) for x in allBugs])
        allBugsHashes = set([x[2] for x in allBugs])
        new = [{'reportId': hashToIdDict[x]} for x in list(uniqueHashes - allBugsHashes)]
        return new
    
    def clean(self):
        cmd = 'cd {0} && make clean'.format(self.repo)
        self.runCmdClean(cmd)
    
    def getDataAfterInfoLog(self, text):
        lines = text.split('\n')
        if len(lines) > 2:
            return lines[1]
        return ''
    
    def runCmd(self, cmd):
        command = '. ' + config.getCcPath() + config.getCcRelativeVenv() + ' && cd ' + config.getCcPath() + config.getCcRelativeBinPath() + ' && ./' + cmd
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        proc_stdout = process.communicate()[0].strip()
        return proc_stdout
    
    def runCmdClean(self, cmd):
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        proc_stdout = process.communicate()[0].strip()
        return proc_stdout