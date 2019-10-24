#!/usr/bin/python
from sciath.job import Job
from sciath.job import JobDAG
from sciath.launcher import Launcher

def example_1():
    print('++++++++ Launcher example 1 ++++++++')
    job_launcher = Launcher()
    job_launcher.setVerbosityLevel(1000)

    # Example usage
    jA = Job(['echo','random-text-from-example_1'],name='DMDA interpolation')
    jA.setResources(ranks=4,threads=1)
    job_launcher.submitJob(jA,path='./')
    #job_launcher.clean(jA,path='./')

def example_2():
    print('++++++++ Launcher example 2 (DAG with dependencies define by a non-trival graph) ++++++++')

    # Example usage
    jA = JobDAG(['echo', '\"random-text-from-example_2\"'],name='jobA')
    jA.setResources(threads=1,ranks=2)

    jdb = Job( ['echo', '\"dependent job b\"'], name = 'b' )
    jdc = Job( ['echo', '\"dependent job c\"'], name = 'c' )
    jdd = Job( ['echo', '\"dependent job d\"'], name = 'd' )
    jdd.setResources(threads=1,ranks=4)
    jde = Job( ['echo', '\"dependent job e\"'], name = 'e' )
    jdf = Job( ['echo', '\"dependent job f\"'], name = 'f' )
    jdg = Job( ['echo', '\"dependent job g\"'], name = 'g' )
    jdh = Job( ['echo', '\"dependent job h\"'], name = 'h' )

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


    job_launcher = Launcher()
    job_launcher.setVerbosityLevel(1)

    job_launcher.submitJob(jA,path='./')
    #job_launcher.clean(jA,path='./')

def example_3():
    print('++++++++ Launcher example 3 ++++++++')
    job_launcher = Launcher()
    job_launcher.setVerbosityLevel(1000)
    
    # Example usage
    #jA.setResources(ranks=4,threads=1)
    job_launcher.submitJob(
                           Job( ['echo','random-text-from-example_3'],
                                name='DMDA interpolation',
                                mpiranks=14,threads=4,wall_time=0.5),
                           path = './')




#example_1()
example_2()
#example_3()

