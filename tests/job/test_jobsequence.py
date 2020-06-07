#!/usr/bin/env python
from __future__ import print_function

from sciath.job import Job
from sciath.job import JobSequence


resources_to_print = ['mpiranks','idlempirankspernode','threads']

# Example usage
jA = JobSequence('echo \"job A\"',name='DMDA interpolation <exec 4>')
jA.setResources(ranks=4,threads=11)

jB = Job('echo \"dependent job 1 <exec 3>\"')
jB.setResources(ranks=140)

jC = Job('echo \"dependent job 2 <exec 2>\"')

jD = Job('echo \"dependent job 3 <exec 1>\"', exitCode=0) # Job which will run first
jD.setResources(threads=27,ranks=40)

jA.append(jB)
jA.append(jC)
jA.append(jD)

er = jD.createExecuteCommand()
print('Execute command + resources for jD')
for i in er:
    print('  cmd =',i[0])
    for r in resources_to_print:
        print(' ',r,':',i[1][r])

er = jA.createExecuteCommand()
print('Execute command + resources for jA')
for i in er:
    print('  cmd =',i[0])
    for r in resources_to_print:
        print(' ',r,':',i[1][r])

print('Resources required for jD:      name =',jD.name,' :')
for r in resources_to_print:
    print(r,':',jD.getResources()[r])
print('Max. resources required for jD: name =',jD.name,' :')
for r in resources_to_print:
    print(r,':',jD.getMaxResources()[r])


print('Resources required for jA:      name =',jA.name,' :')
for r in resources_to_print:
    print(r,':',jA.getResources()[r])
print('Max. resources required for jA: name =',jA.name,' :')
for r in resources_to_print:
    print(r,':',jA.getMaxResources()[r])
