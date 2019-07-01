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
