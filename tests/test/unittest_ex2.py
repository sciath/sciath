#!/usr/bin/env python
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

def test1_ud(): # result: pass
    cmd = ['sh' , 'write_test1_ud.sh' ]
    
    t = Test( Job(cmd), 'Test_1_ud', path = OUTPUT_PATH )
    print(t.output_path)
    t.verifier = VerifierUnixDiff(t, "./expected/t1.expected")

    job_launcher.submitJob( t.job, path = t.output_path )
    t.verify()
    t.print()
    return t

def test2_ud(): # result: fail
    cmd = ['sh' , 'write_test2_ud.sh' ]
    
    t = Test( Job(cmd), 'Test_2_ud', path = OUTPUT_PATH )
    t.verifier = VerifierUnixDiff(t, "./expected/t1.expected" )
    
    job_launcher.submitJob( t.job, path = t.output_path )
    t.verify()
    t.print()
    return t



def main():
    try:
        os.mkdir(OUTPUT_PATH)
    except:
        pass

    # test using unix-diff verifierr
    t1_ud = test1_ud()
    t2_ud = test2_ud()
  

    tests = [t1_ud,t2_ud]
    for t in tests:
        job_launcher.clean(t.job, path = t.output_path)

main()
