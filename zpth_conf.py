
class zpthBatchQueuingSystem:
  accountName = []
  queueName = []
  mpiLaunch = []
  queuingSystemType = []
  #  ignoreKeywords = [ '#', '!', '//', '*' ]
  jobSubmissionCommand = []

  def __init__(self):
    self.data = []


#  def addIgnoreKeywords(self,d):
#    self.ignoreKeywords.append(d)


  def setQueueName(self,name):
    self.queueName = name


  def setHPCAccountName(self,name):
    self.accountName = name


  def setMPILaunch(self,name):
    self.mpiLaunch = name


  def setQueueSystemType(self,type):
    if type in ['PBS','pbs']:
      self.queuingSystemType = 'pbs'
      self.jobSubmissionCommand = 'qsub'
      print('Recognized PBS queuing system')

    elif type in ['LSF','lsf']:
      self.queuingSystemType = 'lsf'
      self.jobSubmissionCommand = 'bsub <'
      print('Recognized LSF queuing system')

    elif type in ['SLURM','slurm']:
      self.queuingSystemType = 'slurm'
      self.jobSubmissionCommand = 'sbatch'
      print('Recognized Slurm queuing system')

    elif type in ['LoadLeveler','load_leveler','loadleveler','llq']:
      self.queuingSystemType = 'load_leveler'
      self.jobSubmissionCommand = 'llsubmit'
      print('Recognized IBM LoadLeveler queuing system')

    else:
      print('Value found: ' + type + ' ...')
      raise ValueError('Unknown or unsupported batch queuing system specified')


  def setQueueName(self,name):
    self.queueName = name


  def view(self):
    print('zpthBatchQueuingSystem:')
    print('  System:        ',self.queuingSystemType)
    print('  Submit command:', self.jobSubmissionCommand)
    print('  MPI launcher:    ',self.mpiLaunch)
    if self.accountName:
      print('  Account:       ',self.accountName)
    if self.queueName:
      print('  Queue:         ',self.queueName)


  def configure(self):
    print('Creating new .conf file')
    v = input('Batch queuing system type <pbs,lsf,slurm,llq>: ')
    if not v:
      raise ValueError('You must specify the type of queuing system')
    self.setQueueSystemType(v)

    v = input('MPI launch command (required): ')
    if not v:
      raise ValueError('You must specify an MPI launch command')
    self.setMPILaunch(v)

    v = input('Account to charge (optional - hit enter if not applicable): ')
    self.setHPCAccountName(v)

    v = input('Queue name to submit tests to (optional - hit enter if not applicable): ')
    self.setQueueName(v)
    
    self.writeDefinition()


  def reconfigure(self):
    try:
      self.loadDefinition()
    
    except:
      print('Creating new .conf file')
      v = input('Batch queuing system type <pbs,lsf,slurm,llq>: ')
      if not v:
        raise ValueError('You must specify the type of queuing system')
      self.setQueueSystemType(v)
      
      v = input('MPI launch command (required): ')
      if not v:
        raise ValueError('You must specify an MPI launch command')
      self.setMPILaunch(v)
      
      v = input('Account to charge (optional - hit enter if not applicable): ')
      self.setHPCAccountName(v)
      
      v = input('Queue name to submit tests to (optional - hit enter if not applicable): ')
      self.setQueueName(v)
      
      self.writeDefinition()


  def writeDefinition(self):

    file = open('zpthBatchQueuingSystem.conf','w')
    #    file.write('queuingSystemType = ' + self.queuingSystemType + '\n' )
    #    file.write('accountName = ' + self.accountName + '\n' )
    #    file.write('queueName = ' + self.queueName + '\n' )
    #    file.write('mpiLaunch = ' + self.mpiLaunch + '\n' )
    file.write( self.queuingSystemType + '\n' )
    file.write( self.mpiLaunch + '\n' )
    file.write( self.queueName + '\n' )
    file.write( self.accountName + '\n' )
    file.close()


  def loadDefinition(self):
    try:
      file = open('zpthBatchQueuingSystem.conf','r')
      print('Loading from file')

      v = file.readline()
      self.setQueueSystemType(v.rstrip())

      v = file.readline()
      self.setMPILaunch(v.rstrip())

      v = file.readline()
      self.setQueueName(v.rstrip())

      v = file.readline()
      self.setHPCAccountName(v.rstrip())

      file.close()
    except:
      raise ValueError('You must execute configure(), and or writeDefinition() first')

# < end class >

batch = zpthBatchQueuingSystem()
batch.configure()
batch.view()

batch2 = zpthBatchQueuingSystem()
batch2.reconfigure()

#conf.addIgnoreKeywords('**')
#print(conf.ignoreKeywords)

#batch.setQueueSystemType('llq')
#batch.setMPILaunch('mpiexec')
#batch.setHPCAccountName('geophys')
#batch.setQueueName('small')

batch2.view()

