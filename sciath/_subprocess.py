

import sys
import subprocess as subp

def run(command,stdoutFile,stderrFile) :
  if stdoutFile is None:
      stdoutFile = subp.PIPE
  if stderrFile is None:
      stderrFile = subp.PIPE

  if sys.version_info[0] == 2 :
      errorno = subp.call(command,stdout=stdoutFile,stderr=stderrFile)
  else :
      ctx = subp.run(command,universal_newlines=True,stdout=stdoutFile,stderr=stderrFile)
      errorno = ctx.returncode
  return errorno
