
#!/usr/bin/python
import os

from sciath.job import Job
from sciath.job import JobSequence
from sciath.job import JobDAG
from sciath.launcher import Launcher
from sciath.test import Test
from sciath.verifier_unixdiff import VerifierUnixDiff

OUTPUT_PATH = './output'
VERBOSITY = 0
job_launcher = Launcher()
job_launcher.setVerbosityLevel(VERBOSITY)

# Default verifier (check error code(
def test1(): # result: pass
    cmd = ['echo' , '"aBc";' , 'echo' '"kspits=30"' , 'echo ""' ]
  
    t = Test( Job(cmd), 'Test_1', path = OUTPUT_PATH )
    job_launcher.submitJob( t.job, path = OUTPUT_PATH )
    t.verifier.execute()
    t.print()
    return t

def test2(): # result: pass
    cmd = ['echo' , '"aBc";' , 'echo' '"kspits=30"' ]
    
    t = Test( Job(cmd), 'Test_2', path = OUTPUT_PATH )
    job_launcher.submitJob( t.job, path = OUTPUT_PATH )
    t.verifier.execute()
    t.print()
    return t

def test3(): # result: fail
    cmd = ['echo' , '"aBc";' , 'echo' '"kspits=30"' ]
    
    t = Test( Job(cmd,exitCode = 1), 'Test_3', path = OUTPUT_PATH )
    job_launcher.submitJob( t.job, path = OUTPUT_PATH )
    t.verifier.execute()
    t.print()
    return t

def test1_ud(): # result: pass
  cmd = ['sh' , 'write_test1_ud.sh' ]
    
  t = Test( Job(cmd), 'Test_1_ud', path = OUTPUT_PATH )
  print(t.output_path)
  t.verifier = VerifierUnixDiff(t, "./expected/t1.expected")
  
  job_launcher.submitJob( t.job, path = OUTPUT_PATH )
  t.verifier.execute()
  t.print()
  return t

def test2_ud(): # result: fail
  cmd = ['sh' , 'write_test2_ud.sh' ]
  
  t = Test( Job(cmd), 'Test_2_ud', path = OUTPUT_PATH )
  t.verifier = VerifierUnixDiff(t, "./expected/t1.expected" )
  
  job_launcher.submitJob( t.job, path = OUTPUT_PATH )
  t.verifier.execute()
  t.print()
  return t



def main():
  os.mkdir(OUTPUT_PATH)
  
  t1 = test1()
  t2 = test2()
  t3 = test3()

  t1_ud = test1_ud()
  t2_ud = test2_ud()

  tests = [t1,t2,t3 , t1_ud,t2_ud]
  for t in tests:
    job_launcher.clean(t.job, path = OUTPUT_PATH)


main()
