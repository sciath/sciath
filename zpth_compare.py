
import numpy as np
import math as math

def compareLiteral(input,expected):
  print(len(input))

  if len(input) != len(expected):
    print("<compareLiteral failed>: input and expected are of different length");
    print("  expected:",expected)
    print("  input:   ",input)

  for index in range(0,len(expected)):
    if input[index] != expected[index]:
      print("<compareLiteral failed>")
      print("  expected:",expected)
      print("  input:   ",input)
      print("  index[" + str(index) +  "]" + " input" ,  input[index] , ": expected " , expected[index]);

def compareFloatingPoint(input,tolerance,expected):
  if len(input) != len(expected):
    print("<compareFloatingPoint failed>: input and expected are of different length");
    print("  expected:",e_f)
    print("  input:   ",i_f)

  tmp = np.array(input)
  i_f = tmp.astype(np.float)
  tmp = np.array(expected)
  e_f = tmp.astype(np.float)
  tol_f = float(tolerance)

  for index in range(0,len(e_f)):
    absdiff = np.abs(i_f[index] - e_f[index]);
    if absdiff > tol_f:
      print("<compareFloatingPoint failed>: tolerance " + str(tol_f), "not satisifed")
      print("  expected:",e_f)
      print("  input:   ",i_f)
      print("  index[" + str(index) + "]" + " input" ,  i_f[index] , ": expected " , e_f[index], "(+/-"+str(tol_f)+")"  )

def compareInteger(input,tolerance,expected):
  if len(input) != len(expected):
    print("<compareInteger failed>: input and expected are of different length");
    print("  expected:",e_i)
    print("  input:   ",i_i)

  tmp = np.array(input)
  i_i = tmp.astype(np.int)
  tmp = np.array(expected)
  e_i = tmp.astype(np.int)
  tol_i = int(tolerance)
  
  for index in range(0,len(e_i)):
    absdiff = np.abs(i_i[index] - e_i[index]);
    if absdiff > tol_i:
      print("<compareInteger failed>: tolerance " + str(tol_i), "not satisifed")
      print("  expected:",e_i)
      print("  input:   ",i_i)
      print("  index[" + str(index) + "]" + " input" ,  i_i[index] , ": expected " , e_i[index] , "(+/-"+str(tol_i)+")" )


def generateLaunch_PBS(accountname,queuename,testname,executable,ranks,ranks_per_node,walltime):
  if not ranks:
    print("<generateLaunch_PBS>: Requires the number of MPI-ranks be specified")
  if not walltime:
    print("<generateLaunch_PBS>: Requires the walltime be specified")

  print("# ZPTH: auto-generated pbs file")
  print("#!/bin/bash")

  if accountname:
    print("#PBS -A " + accountname) # account to charge
  print("#PBS -N \"" + testname + "\"") # jobname
  print("#PBS -o " + testname + ".stdout")
  print("#PBS -e " + testname + ".stderr")

  if queuename:
    print("#PBS -q " + queuename)

  print("#PBS -l mppwidth=1024,walltime=" + str(walltime))

  print("aprun -B " + executable) # launch command


def generateLaunch_SLURM(accountname,queuename,testname,executable,ranks,ranks_per_node,walltime):
  if not ranks:
    print("<generateLaunch_SLURM>: Requires the number of MPI-ranks be specified")
  if not walltime:
    print("<generateLaunch_SLURM>: Requires the walltime be specified")

  print("# ZPTH: auto-generated slurm file")
  print("#!/bin/bash -l")

  if accountname:
    print("#SBATCH --account=" + accountname + "") # account to charge
  print("#SBATCH --job-name=\"" + testname + "\"") # jobname

  print("#SBATCH --output=" + testname + ".stdout") # jobname.stdout
  print("#SBATCH --error=" + testname + ".stderr") # jobname.stderr

  if queuename:
    print("#SBATCH --partition=" + queuename)

  print("#SBATCH --ntasks=" + str(ranks))
  if ranks_per_node:
    print("#SBATCH --ntasks-per-node=" + str(ranks_per_node))

  print("#SBATCH --time=" + walltime)

  print("aprun -n " + executable) # launch command


def generateLaunch_LSF(accountname,queuename,testname,executable,ranks,rusage,walltime):
  if not ranks:
    print("<generateLaunch_LSF>: Requires the number of MPI-ranks be specified")
  if not walltime:
    print("<generateLaunch_LSF>: Requires the walltime be specified")
  
  print("# ZPTH: auto-generated lsf file")
  print("#!/bin/sh")
  
  print("#BSUB -J " + testname ) # jobname
  
  print("#BSUB -o " + testname + ".stdout") # jobname.stdout
  print("#BSUB -e " + testname + ".stderr") # jobname.stderr
  
  if queuename:
    print("#BSUB -q " + queuename)
  
  print("#BSUB -n " + str(ranks))

  if rusage:
    print("#BSUB -R \'" + rusage + "\'")

  print("#BSUB -W " + walltime)
  
  print("aprun -n " + executable) # launch command


def generateLaunch_LoadLevelerBG(accountname,queuename,testname,executable,total_ranks,machine_ranks_per_node,walltime):
  if not total_ranks:
    print("<generateLaunch_LoadLeveler>: Requires the number of MPI-ranks be specified")
  if not walltime:
    print("<generateLaunch_LoadLeveler>: Requires the walltime be specified")

  print("# ZPTH: auto-generated llq file")

  print("#!/bin/sh")
  print("# @ job_name = " + testname)
  print("# @ job_type = bluegene")
  print("# @ error = $(job_name)_$(jobid).stderr")
  print("# @ output = $(job_name)_$(jobid).stdout")
  print("# @ environment = COPY_ALL;")
  print("# @ wall_clock_limit = " + str(walltime))
  print("# @ notification = never")
  print("# @ class = " + queuename)

  bgsize = math.ceil(total_ranks/machine_ranks_per_node)
  print("# @ bg_size = " + str(bgsize))
  print("# @ bg_connection = TORUS")
  print("# @ queue")

  print("runjob -n " + executable) # launch command


# Queue config requires:
#   - mpilaunch command, e.g. mpirun, mpieec, aprun, srun
#   - account name
#   - queue name
#   - machine specs (ranks-per-node)

# A job to be launched requires:
#   - job name
#   - number of ranks
#   - number of ranks per node (optional)
#   - walltime
#   - memory usage (optional)


def main():
  print("Test compare")

  input = [[ "a", "bb", "cc" ], ['aa']]
  expected = [[ "a", "bb", "cc" ], ['aaz'] ]
  compareLiteral(input,expected)

  input = [ "0.1", "0.44" ]
  expected = [ "0.1", "0.445" ]
  compareFloatingPoint(input,0.001,expected)

  input = [ "2", "44" ]
  expected = [ "5", "44" ]
  compareInteger(input,2,expected)

#  generateLaunch_PBS('geofysisk','testing','zpth-ex1','ex1',2,'1',"00:05:00")
#  generateLaunch_SLURM('geofysisk','testing','zpth-ex1','ex1',2,'1',"00:05:00")
#  generateLaunch_LSF('geofysisk','testing','zpth-ex1','ex1',2,"span[ptile=4] rusage[mem=6000]","00:05:00")
  generateLaunch_LoadLevelerBG('geofysisk','testing','zpth-ex1','ex1',41,40,"00:05:00")

if __name__ == "__main__":
  main()

