
from sciath.sjob import SJob


# Example usage
jA = SJob('echo \"job A\"',name='DMDA interpolation')
jA.setResources(ranks=4,threads=11)

jB = SJob('echo \"dependent job 1\"')
jB.setResources(ranks=140)

jC = SJob('echo \"dependent job 2\"')

jD = SJob('echo \"dependent job 3\"',description='Job which will be run first',exitCode=0)
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

