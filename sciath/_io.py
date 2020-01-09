import sys

def py23input(prompt) :
    if sys.version_info[0] == 2 :
        v = raw_input(prompt)
    else :
        v = input(prompt)
    return(v)

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

# verbosity-regulated printing
def printv(level,verbosityLevel,*vargs):
    if level >= verbosityLevel:
        line = ''
        N = len(vargs)
        for i in range(N-1):
            line += str(vargs[i])
            line += ' '
        line += str(vargs[N-1])
        print(line)

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
