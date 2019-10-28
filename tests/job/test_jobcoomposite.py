
#!/usr/bin/python
from sciath.job import Job
from sciath.job import JobSequence
from sciath.job import JobDAG

def create_seq(prefix):
    # Example usage
    jA = JobSequence(['echo','job-'+prefix],name='job-seq-'+prefix)
    jB = Job(['echo','job-1'+prefix],name='d-j1-'+prefix)
    jC = Job(['echo','job-2'+prefix],name='d-j2-'+prefix)
    jD = Job(['echo','job-3'+prefix],name='d-j3-'+prefix)
    jA.append(jB)
    jA.append(jC)
    jA.append(jD)
    return jA

# Sequence - Sequence
def create_composite_seq():
    s1 = create_seq("A")
    s2 = create_seq("B")
    
    s1.append(s2)

    print('============================================================================')
    s1.view()
    print('============================================================================')
    er = s1.createExecuteCommand()
    print('Execute command + resources for jA')
    for i in er:
        print('  cmd =',i[0],'res =',i[1])


# DAG - Sequence
def create_dag_sequence():
    # Example usage
    jA = JobDAG('echo \"job A\"',name='jobDAG')
    jdb = Job( 'echo \"dependent job b\"', name = 'b' )
    jdc = Job( 'echo \"dependent job c\"', name = 'c' )
    jdd = create_seq('d')
    
    jA.registerJob(jdb)
    jA.registerJob(jdc)
    jA.registerJob(jdd)


    dag = { 'jobDAG': ( 'b' ),
          'b': ( 'c' ,'job-seq-d'),
          'c': ([None]),
          'job-seq-d' : ([None]),
        }
    jA.insert(dag)
    
    print('============================================================================')
    jA.view()
    print('============================================================================')
    er = jA.createExecuteCommand()
    print('Execute command + resources for jA')
    for i in er:
        print('  cmd =',i[0],'res =',i[1])


#create_composite_seq()
create_dag_sequence()

