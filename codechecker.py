from config import config

import subprocess
import sys
import json

class CodeChecker():
    def __init__(self, repo = None):
        if repo is None:
            self.repo = config.getRepoDir()
        else:
            self.repo = repo
    
    def check(self, clean = False):
        if clean:
            cmd = 'cd {0} && make clean'.format(self.repo)
            self.runCmd(cmd)
        jobs = ''
        if config.ccNoOfJobs > 1:
            jobs = ' -j {0}'.format(config.ccNoOfJobs)
        checkers = '-e all'
        #if len(config.customCheckers) > 0:
        #    checkers = '-d all -e {0}'.format(' -e '.join(config.customCheckers.split(',')))
        cmd = 'CodeChecker check {0} -e all -b "cd {1} && make {0}" -o {2}'.format(jobs, self.repo, config.getTmpDir())
        self.runCmd(cmd)
    
    def store(self, tag):
        cmd = 'CodeChecker store {0} -n {1} --tag {2}'.format(config.getTmpDir(), config.getCcRunName(), tag)
        self.runCmd(cmd)
    
    def diffResolved(self, baseRun, newRun):
        cmd = 'CodeChecker cmd diff -b {0} -n {1} --resolved -o json'.format(baseRun, newRun)
        stdoutData = self.runCmd(cmd).decode(sys.stdout.encoding)
        output = self.getDataAfterInfoLog(stdoutData)
        out = []
        try:
            out = json.loads(output)
        except json.decoder.JSONDecodeError:
            pass
        return out
    
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