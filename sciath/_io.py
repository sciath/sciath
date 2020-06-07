import os
import sys
if os.name == 'posix' and sys.version_info[0] < 3:
    import subprocess32 as subprocess # To be removed once Python 2 is fully abandoned
else:
    import subprocess

def py23input(prompt) :
    if sys.version_info[0] == 2 :
        v = raw_input(prompt)
    else :
        v = input(prompt)
    return(v)

def _remove_file(file2rm, safetyMode=False, debugMode=False):
    """ Remove a file, with some debugging options for development purposes """
    if os.path.isfile(file2rm) :
        cmd = ['rm',file2rm]
        if safetyMode:
            cmd = ['rm','-i',file2rm]
        if debugMode:
            print('  removing file: ',file2rm)
            print('  ',cmd)
        else:
            subprocess.call(cmd)

def command_join(command):
    """ Convert a command (as would go to subprocess.run()) to a copy-pasteable string

    Do something similar to shlex.join (Python 3.8+), attempting to quote arguments
    that contain spaces, and escape newlines in the result. """

    joined = ' '.join(["'"+term+"'" if ' ' in term else term for term in command])
    joined = joined.replace('\n','\\n')
    return joined

class NamedColors:
    def __init__(self):
        self.set_colors()

    def set_colors(self,use_bash=True):
        self.HEADER    = '\033[35m' if use_bash else ''
        self.SUBHEADER = '\033[36m' if use_bash else ''
        self.OK        = '\033[32m' if use_bash else ''
        self.WARNING   = '\033[93m' if use_bash else ''
        self.FAIL      = '\033[91m' if use_bash else ''
        self.ENDC      = '\033[0m'  if use_bash else ''
        self.BOLD      = '\033[1m'  if use_bash else ''
        self.UNDERLINE = '\033[4m'  if use_bash else ''

# two space tab for formatted print statements
tab = '  '


def dictView(d):
    if isinstance(d,dict):
        string = '{'
        for key in sorted(d):
            value = d[key]
            string += "'" + str(key) + "': " + str(value) + ", "
        string = string[:-2] # remove last two characters - yes, I could have used a generator...
        string += '}'
        return string
    else:
        print('[SciATH error] dictView() requires a dictionary as input.')
        sys.exit(1)
