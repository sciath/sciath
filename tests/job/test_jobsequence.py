#!/usr/bin/env python
from sciath.job import Job
from sciath.job import JobSequence


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
  print('  cmd =',i[0],'res =',i[1])

er = jA.createExecuteCommand()
print('Execute command + resources for jA')
for i in er:
  print('  cmd =',i[0],'res =',i[1])

print('Resources required for jD:      name =',jD.name,' :',jD.getResources())
print('Max. resources required for jD: name =',jD.name,' :',jD.getMaxResources())
print('============================================================================')
jD.view()
print('============================================================================')


print('Resources required for jA:      name =',jA.name,' :',jA.getResources())
print('Max. resources required for jA: name =',jA.name,' :',jA.getMaxResources())
print('============================================================================')
jA.view()
print('============================================================================')

