
import sys
# Only use the OrderedDict() class from collections - specifically this is only important
# to use if we intend to use the result of SJob.view() for testing
import collections

# two space tab for formmated print statements
tab = '  '

# verbosity regulated printing
def printv(level,verbosityLevel,*vargs):
  if level >= verbosityLevel:
    line = ''
    N = len(vargs)
    for i in range(N-1):
      line += str(vargs[i])
      line += ' '
    line += str(vargs[N-1])
    print(line)


# module private viewer
def _dictView(d):
  if isinstance(d,dict) or isinstance(d,OrderedDict):
    string = '{'
    for key in d:
      value = d[key]
      string += "'" + str(key) + "': " + str(value) + ", "
    string = string[:-2] # remove last two characters - yes, I could have used a generator...
    string += '}'
    return string
  else:
    print('[SciATH error] dictView() requires a dictionary as input.')
    sys.exit(1)


class SJob:
  """
  A SciARTH job
    
  Args:
    cmd          (string): The command used to execute your application
    **kwargs (name=value): A keyword argument list
                           The SJob constructor will recognize the following namee:
                             name        (string): textual name you want to assign to the job
                             description (string): desciption of what the job does
                             exitCode       (int): the exit code which should be used to infer success
  Examples:
    job = SJob('echo \\"hi\\"') -> a new job which will simply execute $echo 'hi'
    
    job = SJob('echo \\"hi\\"',**kwargs,) -> a new job which will simply execute $echo "hi"
                                       and with variables initialized with the name=value pairs
    job = SJob('echo \\"hi\\"', name='job-1', description='My first SciARTH job', exitCode=0)
  
  """
  def __init__(self,cmd,**kwargs):
    self.cmd      = cmd # command which will be executed via a system call to run this job
    self.child    = None
    # Design note: we use a dict to enable developers to easily add support for different resource requests
    self.resources = collections.OrderedDict()
    self.resources.update({"mpiranks":1}) # mpi parallel resource data
    self.resources.update({"threads":1}) # thread parallel (e.g. OMP) resource data

    # optional info not needing a setter (e.g. they are not special enough)
    self.name              = ''
    self.description       = ''
    self.exit_code_success = 0
  
    for key, value in kwargs.items():
      if key == 'name':
        self.name = value
      if key == 'description':
        self.description = value
      if key == 'exitCode':
        self.exit_code_success = int(value)


  def setChildJob(self,child):
    """
    Allows one to attach a dependent (child) SJob instance which will
    be executed prior to the current (parent) SJob instance.
    There is no limit to the depth of the parent->child tree.
    """
    
    if not isinstance(child,SJob):
      print('[SciATH error] Nested job is invalid.')
      print('               Child job must be of type SJob and not',type(child))
      sys.exit(1)
    self.child = child


  def __getMaxResourcesRecursive(self,max):
    # iterate through keys in self.resources, update values in max
    for key in self.resources:
      value = self.resources[key]
      if value > max[key]:
        max.update({key:value})
    if self.child != None:
      max = self.child.__getMaxResourcesRecursive(max)
    return max
    
  def getMaxResources(self):
    """
    Returns a dict() defining the maximum required counts / values 
    for each valid resource associated with a job.
    The maximum is compute over the parent and any child jobs.
    Such functionality is required for batch queue systems.
    """
    
    # Iterate through keys in self.resource, set initial values in max
    # We are certain no new keys will be added as setResources() will
    # error if unrecognized resources were requested
    max = collections.OrderedDict()
    for key in self.resources:
      value = self.resources[key]
      max.update({key:value})
    
    if self.child != None:
      max = self.child.__getMaxResourcesRecursive(max)
    return max

  def getResources(self):
    """
    Returns a dict() defining the compute resources required for this job.
    This method will ignore any resources requested by a child job.
    """
    
    return self.resources

  def __createExecuteCommandRecursive(self):
    """
    Returns a list of commands, resources by decending through the job parent->child tree.
    """
    
    execute = []
    resources = []
    if self.child != None:
      e,r = self.child.__createExecuteCommandRecursive()
      execute += e
      resources += r
    execute.append(self.cmd)
    resources.append(self.resources)
    return execute,resources

  def createExecuteCommand(self):
    """
    Returns a list of command, resource tuples.
    To preserve the order dependent of the parent->child relationship, 
    the commands should be executed in order from first to last.
    """
    
    execute,resources = self.__createExecuteCommandRecursive()
    ex = []
    for i in range(len(execute)):
      ex.append( (execute[i],resources[i]) )
    return ex

  def setResources(self,**kwargs):
    """
    Define job resources (e.g. number of mpi ranks) via "resource_name"=number keyword=value pairs
    The keywords used to identify the number mpi ranks is ['ranks', 'Ranks', 'mpiranks', 'MPIRanks'].
    The keywords used to identify the number of threads is ['threads', 'ompthreads'].
    Unrecognized resource types will produce an error.
    """
    
    # Valid names to identify number of MPI ranks
    ranks_k = [ 'ranks', 'Ranks', 'mpiranks', 'MPIRanks' ]
    ranks_set = 0
    
    # Valid names to identify number of threads
    threads_k = [ 'threads', 'ompthreads' ]
    threads_set = 0
    
    # Others resources go here

    # Join all valid name list and check that the provided keyword is a valid resource name / identifier
    allValidResourceNames = ranks_k + threads_k
    for key,value in kwargs.items():
      if key not in allValidResourceNames:
        print('[SciATH error]: Unknown resource type \"' + str(key) + '\" was requested.')
        print('                Choose from the following:',allValidResourceNames)
        sys.exit(1)

    for key, value in kwargs.items():
      if key in ranks_k: # look mpi rank keyword identifiers
        self.resources.update({"mpiranks":int(value)})
        ranks_set += 1
      
      if key in threads_k: # look thread keyword identifiers
        self.resources.update({"threads":int(value)})
        threads_set += 1

    # Sanity check that only one instance of a valid keyword
    # for a given resource type (e.g. mpi ranks) was provided
    if ranks_set > 1:
      print('[SciATH error]: More than one instance of a valid MPI ranks keyword was provided to setResources().')
      print('                To set the #mpi ranks, choose one of:',ranks_k)
      sys.exit(1)
    
    if threads_set > 1:
      print('[SciATH error]: More than one instance of a valid threads keyword was provided to setResources().')
      print('                To set the #threads, choose one of:',threads_k)
      sys.exit(1)


  def __view_tree(self,indent):
    if self.name != '':
      print(tab*indent + 'Job name:',self.name)
    if self.description != '':
      print(tab*indent + 'Description:',self.description)
    print(tab*indent + 'Command:',self.cmd)
    print(tab*indent + 'Exit code success:',self.exit_code_success)
    #print(tab*indent + 'MPI ranks:',self.resources["mpiranks"],', Threads:',self.resources["threads"])
    print(tab*indent + 'Resources:',_dictView(self.resources))
    if self.child != None:
      print(tab*indent + 'Dependency:')
      self.child.__view_tree(indent+1)
    else:
      print(tab*indent + 'No dependencies')

  def view(self):
    """
    Display the contents of an SJob instance to stdout.
    The parent->child relationship will be reported.
    Uninitialized non-essential members will not be reported.
    This includes: self.name; self.description; self.child.
    """
    
    if self.name != '':
      print('Job name:',self.name)
    if self.description != '':
      print('Description:',self.description)
    print('Command:',self.cmd)
    print('Exit code success:',self.exit_code_success)
    #print('MPI ranks:',self.resources["mpiranks"],', Threads:',self.resources["threads"])
    print('Resources:',_dictView(self.resources))
    maxR = self.getMaxResources()
    print('Max. resources (incl. dependencies):', _dictView(maxR))
    if self.child != None:
      print('Dependency:')
      self.child.__view_tree(1)
    else:
      print('No dependencies')

