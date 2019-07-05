
from sciath.sjob import SJob
from sciath.sjob import SJobSequence
from sciath.sjob import SJobDAG


def example0a():
  print('++++++++ example 0a ++++++++')
  
  jd1 = SJob( 'echo \"dependent job 1\"', name = 'demo-job-1' )
  jd2 = SJob( 'echo \"dependent job 2\"')

  
  # Example usage
  jA = SJobDAG('echo \"job A\"',name='DAG with no deps.')
  jA.registerJob(jd1)
  jA.registerJob(jd2)
  jA.view()

def example1():
  print('++++++++ example 1 (DAG with no deps.) ++++++++')
  
  # Example usage
  jA = SJobDAG('echo \"job A\"',name='jobA')

  user_dag = {'jobA': [None]}
  jA.insert(user_dag)

  er = jA.createExecuteCommand()
  print('Execute command + resources for jA')
  for i in er:
    print('  cmd =',i[0],'res =',i[1])

  print('============================================================================')
  jA.view()
  print('============================================================================')


def example2():
  print('++++++++ example 2 (DAG with one dep.) ++++++++')

  # Example usage
  jA = SJobDAG('echo \"job A\"',name='jobA')
  jA.setResources(threads=27,ranks=40)

  jd1 = SJob( 'echo \"dependent job 1\"', name = 'demo-depjob-1' )
  jd1.setResources(threads=101,ranks=101)

  jA.registerJob(jd1)


  user_dag = {'jobA': [ 'demo-depjob-1' ],
              'demo-depjob-1': [None]}

  jA.insert(user_dag)

  er = jA.createExecuteCommand()
  print('Execute command + resources for jA')
  for i in er:
    print('  cmd =',i[0],'res =',i[1])

  print('============================================================================')
  jA.view()
  print('============================================================================')


def example3():
  print('++++++++ example 3 (DAG with dependencies define by a non-trival graph) ++++++++')
  
  # Example usage
  jA = SJobDAG('echo \"job A\"',name='jobA')
  jA.setResources(threads=27,ranks=40)

  jdb = SJob( 'echo \"dependent job b\"', name = 'b' )
  jdc = SJob( 'echo \"dependent job c\"', name = 'c' )
  jdd = SJob( 'echo \"dependent job d\"', name = 'd' )
  jdd.setResources(threads=1,ranks=4)
  jde = SJob( 'echo \"dependent job e\"', name = 'e' )
  jdf = SJob( 'echo \"dependent job f\"', name = 'f' )
  jdg = SJob( 'echo \"dependent job g\"', name = 'g' )
  jdh = SJob( 'echo \"dependent job h\"', name = 'h' )

  jl = [ jdb, jdc, jdd, jde, jdf, jdg, jdh]
  for j in jl:
    jA.registerJob(j)


  dag = {'jobA': [ 'b', 'c', 'h'],
            'b': ('c','f'),
            'c': ('d', 'e', 'f'),
            'd': ('g'),
            'e': ('h'),
            'f': [None],
            'g': ([None]),
            'h': ([None])}

  jA.insert(dag)
  
  er = jA.createExecuteCommand()
  print('Execute command + resources for jA')
  for i in er:
    print('  cmd =',i[0],'res =',i[1])
  
  print('============================================================================')
  jA.view()
  print('============================================================================')



#example0a()

#example1()

#example2()

example3()







