from subprocess import Popen, PIPE
from tempfile import NamedTemporaryFile
import sys
from differ import Differ

class LinuxDiffer(Differ):
    def diff(self, a, b):
        with NamedTemporaryFile() as file:
            file.write(b.encode(sys.stdin.encoding))
            file.flush()
            p = Popen(['diff', '-', file.name], stdin=PIPE, stdout=PIPE, stderr=PIPE)
            out = p.communicate(a.encode(sys.stdin.encoding))[0].strip()
        if p.returncode == 0:
            return ''
        elif p.returncode == 1:
            return out.decode(sys.stdout.encoding)
        else:
            print('error %s' % p.returncode)
            return ''