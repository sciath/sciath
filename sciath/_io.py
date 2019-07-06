import sys

def py23input(prompt) :
  if sys.version_info[0] == 2 :
    v = raw_input(prompt)
  else :
    v = input(prompt)
  return(v)

class NamedColors:
  HEADER    = '\033[35m'
  SUBHEADER = '\033[36m'
  OKGREEN   = '\033[32m'
  WARNING   = '\033[93m'
  FAIL      = '\033[91m'
  ENDC      = '\033[0m'
  BOLD      = '\033[1m'
  UNDERLINE = '\033[4m'

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
