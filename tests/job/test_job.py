#!/usr/bin/env python
from sciath.job import Job


# Example usage
jA = Job('echo \"job A\"',name='DMDA interpolation')
jA.setResources(ranks=4,threads=11)

jB = Job('echo \"dependent job 1\"')
jB.setResources(ranks=140)

jC = Job('echo \"dependent job 2\"')

jD = Job('echo \"dependent job 3\"',exitCode=0) # Job which will run first
jD.setResources(threads=27,ranks=40)

er = jD.createExecuteCommand()
print('Execute command + resources for jD')
for i in er:
  print('  cmd =',i[0],'res =',i[1])

er = jA.createExecuteCommand()
print('Execute command + resources for jA')
for i in er:
  print('  cmd =',i[0],'res =',i[1])

print('Resources required for jA:      name =',jA.name,' :',jA.getResources())
print('Max. resources required for jA: name =',jA.name,' :',jA.getMaxResources())

jA.view()

