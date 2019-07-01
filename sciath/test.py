from __future__ import print_function
import os
import numpy as np
import math as math
import re
from sciath._io import NamedColors as sciathcolors

def compareLiteral(input,expected):
  status = True
  err = ''
  if len(input) != len(expected):
    err = err + "compareLiteral [failed]\nReason: input and expected are of different length\n"
    err = err + ("  expected: %s\n" % expected)
    err = err + ("  input:    %s\n" % input)
    status = False
    return status,err
  for index in range(0,len(expected)):
    if input[index] != expected[index]:
      if status:
        err = err + "compareLiteral [failed]\nReason: strings are different\n"
        err = err + ("  expected: %s\n" % expected)
        err = err + ("  input:    %s\n" % input)
      err = err + "  index[" + str(index) +  "]" + " input \"" +  input[index] + "\" != expected \"" + expected[index] + "\"\n"
      status = False
  return status,err

def compareFloatingPointAbsolute(input,tolerance,expected):
  status = True
  err = ''
  tmp = np.array(input)
  i_f = tmp.astype(np.float)
  tmp = np.array(expected)
  e_f = tmp.astype(np.float)
  tol_f = float(tolerance)
  if len(input) != len(expected):
    err = err + "compareFloatingPointAbsolute [failed]\nReason: input and expected are of different length\n"
    err = err + ("  expected: %s\n" % e_f)
    err = err + ("  input:    %s\n" % i_f)
    status = False
    return status,err
  for index in range(0,len(e_f)):
    absdiff = np.abs(i_f[index] - e_f[index]);
    if absdiff > tol_f:
      if status :
        err = err + "compareFloatingPointAbsolute [failed]\nReason: absolute tolerance " + ("%1.4e" % tol_f) + " not satisfied\n"
        err = err + ("  expected: %s\n" % e_f)
        err = err + ("  input:    %s\n" % i_f)
      err = err + "  index[" + str(index) + "]" + (" input %1.6e" %  i_f[index])  + (" doesn't match expected %1.6e" % e_f[index]) + "\n"
      status = False
  return status,err

def compareFloatingPointRelative(input,tolerance,expected,epsilon=None):
  status = True
  err = ''
  tmp = np.array(input)
  i_f = tmp.astype(np.float)
  tmp = np.array(expected)
  e_f = tmp.astype(np.float)
  tol_f = float(tolerance)
  if len(input) != len(expected):
    err = err + "compareFloatingPointRelative [failed]\nReason: input and expected are of different length\n"
    err = err + ("  expected: %s\n" % e_f)
    err = err + ("  input:    %s\n" % i_f)
    status = False
    return status,err
  for index in range(0,len(e_f)):
    if epsilon :
      reldiff = np.abs(i_f[index] - e_f[index])/(np.abs(e_f[index]) + epsilon);
    else :
      reldiff = np.abs(i_f[index] - e_f[index])/np.abs(e_f[index]);
    if reldiff > tol_f:
      if status:
        err = err + "compareFloatingPointRelative [failed]\nReason: relative tolerance " + ("%1.4e" % tol_f)
        if epsilon :
          err  = err + ", epsilon " + ("%1.4e" % epsilon) +","
        err = err  + " not satisfied\n"
        err = err + ("  expected: %s\n" % e_f)
        err = err + ("  input:    %s\n" % i_f)
      err = err + "  index[" + str(index) + "]" + (" input %1.6e" %  i_f[index])  + (" doesn't match expected %1.6e" % e_f[index]) + "\n"
      status = False
  return status,err

def compareInteger(input,tolerance,expected):
  status = True
  err = ''
  tmp = np.array(input)
  i_i = tmp.astype(np.int)
  tmp = np.array(expected)
  e_i = tmp.astype(np.int)
  tol_i = int(tolerance)
  if len(input) != len(expected):
    err = err + "compareInteger [failed]\nReason: input and expected are of different length\n"
    err = err + ("  expected: %s\n" % e_i)
    err = err + ("  input:    %s\n" % i_i)
    status = False
    return status,err
  for index in range(0,len(e_i)):
    absdiff = np.abs(i_i[index] - e_i[index]);
    if absdiff > tol_i:
      if status:
        err = err + "compareInteger [failed]\nReason: tolerance " + str(tol_i) + " not satisifed\n"
        err = err + ("  expected: %s\n" % e_i)
        err = err + ("  input:    %s\n" % i_i)
      err = err + "  index[" + str(index) + "]" + (" input \"%s\"" %  i_i[index]) + (" != expected \"%s\"" % e_i[index]) + " (+/-"+str(tol_i)+")\n"
      status = False
  return status,err

def parseFile(filename,keywords):
  flat = ''
  contents = []
  if filename:
    file = open(filename,"r")
    for line in file:
      if line.rstrip():
        if not any(keywords in line for keywords in keywords):
          rm_lb = line.lstrip()
          rm_lb = rm_lb.rstrip()
          flat = flat + (rm_lb + ' ')
          stripped_line = line.rstrip()
          stripped_line = stripped_line.lstrip()
          contents.append(stripped_line)
    file.close()
  return(contents,flat)

def getKeyValues(contents,keyword):
  c1 = contents
  f_c = []
  f_r = []
  f_s = []

  # Look for arrays, then strip them out
  find_curly  = re.findall("\s*" + keyword + "\s*=?\s*[\{].*?[\}]", c1)
  if find_curly:
    f_c  = re.findall("\s*" + keyword + "\s*=?\s*[\{](.*?)[\}]", c1)
    for item in find_curly:
      c1 = c1.replace(item,' ')
  find_round  = re.findall("\s*" + keyword + "\s*=?\s*[\(].*?[\)]", c1)
  if find_round:
    f_r  = re.findall("\s*" + keyword + "\s*=?\s*[\(](.*?)[\)]", c1)
    for item in find_round:
      c1 = c1.replace(item,' ')
  find_square  = re.findall("\s*" + keyword + "\s*=?\s*[\[].*?[\]]", c1)
  if find_square:
    f_s  = re.findall("\s*" + keyword + "\s*=?\s*[\[](.*?)[\]]", c1)
    for item in find_square:
      c1 = c1.replace(item,' ')
  find_single = []
  f_single = re.findall("\s*" + keyword + "\s*=?\s*(.*?)\s", c1)
  list = f_c + f_r + f_s + f_single
  filtered = []
  if list:
    for item in list:
      if item != '':
        trimmed = item.lstrip()
        trimmed = trimmed.rstrip()
        filtered.append(trimmed)
  return filtered

def getKeyValuesAsInt(contents,keyword):
  result = getKeyValues(contents,keyword)
  flattened = []
  for sublist in result:
    if type(sublist) is list:
        pass
    else:
      if sublist != '':
        numlist = sublist.replace(',',' ')
        numlist = numlist.replace(';',' ')
        nums = numlist.split(' ')
        #print(nums)
        for num in nums:
          if num != '':
            flattened.append(num)
  tmp = np.array(flattened)
  values = tmp.astype(np.int)
  return values

def getKeyValuesAsFloat(contents,keyword):
  result = getKeyValues(contents,keyword)
  flattened = []
  for r in result:
    r = r.replace(',',' ')
    r = r.replace(';',' ')
    val = r.split(' ')
    for v in val:
      if v != '':
        flattened.append(v)
  tmp = np.array(flattened)
  values = tmp.astype(np.float)
  return values

def getKeyValuesNLinesInclusive(contents,keyword,numlines):
  result = []
  counter = 0
  start = 0
  for line in contents:
    x = line.find(keyword)
    if x != -1:
      start = counter
      break
    counter = counter + 1
  for index in range(start,start+numlines):
    result.append(contents[index])
  return result

def getKeyValuesNLinesExclusive(contents,keyword,numlines):
  result = []
  counter = 0
  start = 0
  for line in contents:
    x = line.find(keyword)
    if x != -1:
      start = counter + 1
      break
    counter = counter + 1
  for index in range(start,start+numlines):
    result.append(contents[index])
  return result


class Test:
  def __init__(self,name,ranks,execute,expected_file):
    self.passed = -1
    self.walltime = 2.0 # minutes
    self.errormessage = ''
    self.errno = -1
    self.name = name
    if not name or len(name) == 0 :
      raise RuntimeError('Tests must be named')
    self.ranks = ranks
    if isinstance(execute,list):
      self.execute = execute
    if isinstance(execute,str):
      self.execute = [execute]
    self.expected_file = expected_file
    self.keywords = [ '#', '!', '//' ]
    self.output_file = name + '.output'
    self.comparison_file = ''
    self.output_path = ''
    self.sandbox_path = self.name + '_sandbox'
    self.use_sandbox = False
    self.ignore = False
    self.verbosity_level = 1

  def setVerbosityLevel(self,value):
    self.verbosity_level = value

  def verify(self,junk):
    errstr = '[SciAth] A valid verification method for test \"' + self.name + '\" was not found.\n\
              [SciAth] You must provide each test with a method to verify the output.\n\
              [SciAth] The method is set via calling test.setVerifyMethod()'
    raise RuntimeError(errstr)

  def setOutputPath(self,opath):
    self.output_path = opath

  def setComparisonFile(self,fname):
    self.comparison_file = fname

  def setVerifyMethod(self,verify):
    self.verify = verify

  def setWalltime(self,mins):
    self.walltime = mins

  def setUseSandbox(self) :
    self.use_sandbox=True

  def appendKeywords(self,keywords):
    self.keywords.append(keywords)
  #print(self.keywords)

  def getExitCode(self):
    return self.errno

  def getErrorReport(self):
    return self.errormessage

  def getErrorStatus(self):
    return self.passed

  def verifyOutput(self):
    if self.use_sandbox :
      sandboxBack = os.getcwd()
      os.chdir(self.sandbox_path)
    if self.comparison_file == '':
      self.comparison_file = os.path.join(self.output_path,self.output_file)
    if self.verbosity_level > 0:
      print('[Parsing file]',self.comparison_file)
    (self.output_contents,self.output_flatcontents) = parseFile(self.comparison_file,self.keywords)
    if self.use_sandbox :
      os.chdir(sandboxBack)
    if self.verbosity_level > 0:
      print('[Parsing file]',self.expected_file)
    (self.expected_contents,self.expected_flatcontents) = parseFile(self.expected_file,self.keywords)
    self.verify(self)

  def getOutput(self):
    return self.output_contents,self.output_flatcontents

  def getExpected(self):
    return self.expected_contents,self.expected_flatcontents

  def updateStatus(self,status,err):
    if self.passed == -1:
      self.passed = status
      if err != '':
        self.errormessage = self.errormessage + err
      return
    if status == False:
      self.passed = False
      if err != '':
        self.errormessage = self.errormessage + err

  def report(self,type):
    if type == 'summary':
      if self.ignore == True:
        print(sciathcolors.WARNING + ' [' + self.name + ']   skipped' + sciathcolors.ENDC)
      else:
        if self.passed == False:
          print(sciathcolors.FAIL + ' [' + self.name + ']   *** FAILED ***' + sciathcolors.ENDC)
        else:
          print(sciathcolors.OKGREEN + ' [' + self.name + ']   passed' + sciathcolors.ENDC)

    elif type == 'log_short' or type == 'log':
      if self.ignore == False:
        if self.passed == False:
          n = self.name
          ef = self.expected_file
          of = os.path.join(self.output_path,self.output_file)
          num_exec = len(self.execute)
          multiple_exec = num_exec > 1
          if type == 'log_short' :
            if ef :
              print('[' + self.name + '] ' + 'expected file  : ' + ef)
            print('[' + self.name + '] ' + 'output file    : ' + of)
            if multiple_exec :
                for idx,exec_entry in enumerate(self.execute) :
                    print('[' + self.name + '] ' + 'launch command (' + str(idx+1) + '/' + str(num_exec) + ') : ' + str(exec_entry))
            else :
                print('[' + self.name + '] ' + 'launch command :',str(self.execute[0]))
            if len(self.errormessage.split('\n')) < 10:
              print(self.errormessage)
            else:
              print('[' + self.name + '] ' +'  --- please refer to error report log file for full description ---\n')
          elif type == 'log':
            lenheader = 0
            lenheader = max( len(n), len(of) )
            if ef :
              lenheader = max(lenheader,len(ef))
            lenheader += 15 + 2 + 2
            header = lenheader * '='
            print(header)
            print('  test name     : ' + n)
            if ef :
              print('  expected file : ' + ef)
            print('  output file   : ' + of)
            if multiple_exec :
                for idx,exec_entry in enumerate(self.execute) :
                    print('  launch command (' + str(idx+1) + '/' + str(num_exec) + ') : ' + str(exec_entry))
            else :
                print('  launch command:',str(self.execute[0]))
            print('\n' + self.errormessage)
    else:
      print('[' + self.name + '] ' + 'Unknown error log type requested (' + str(type) + ')' )

  def compareFloatingPointAbsolute(self,key,tolerance):
    expected,expected_flat = self.getExpected()
    output,output_flat = self.getOutput()
    values_e = getKeyValuesAsFloat(expected_flat,key)
    if len(values_e) == 0:
      errstr = '[SciAth][VerificationError] Test \"' + self.name + '\" queried the expected file \"' + self.expected_file + '\" for key \"' + key + '\" which was not found. \n\t\t    Users verification code is likely incorrect (contains a typo in the key name)'
      raise RuntimeError(errstr)
    values   = getKeyValuesAsFloat(output_flat,key)
    status,err = compareFloatingPointAbsolute(values,tolerance,values_e)
    kerr = ''
    if status == False:
      kerr = 'Key = \"' + key + '\" --> ' + err
    self.updateStatus(status,kerr)

  def compareFloatingPointRelative(self,key,tolerance,epsilon=None):
    expected,expected_flat = self.getExpected()
    output,output_flat = self.getOutput()
    values_e = getKeyValuesAsFloat(expected_flat,key)
    if len(values_e) == 0:
      errstr = '[SciAth][VerificationError] Test \"' + self.name + '\" queried the expected file \"' + self.expected_file + '\" for key \"' + key + '\" which was not found. \n\t\t    Users verification code is likely incorrect (contains a typo in the key name)'
      raise RuntimeError(errstr)
    values   = getKeyValuesAsFloat(output_flat,key)
    status,err = compareFloatingPointRelative(values,tolerance,values_e,epsilon)
    kerr = ''
    if status == False:
      kerr = 'Key = \"' + key + '\" --> ' + err
    self.updateStatus(status,kerr)

  def compareInteger(self,key,tolerance):
    expected,expected_flat = self.getExpected()
    output,output_flat = self.getOutput()
    values_e = getKeyValuesAsInt(expected_flat,key)
    if len(values_e) == 0:
      errstr = '[SciAth][VerificationError] Test \"' + self.name + '\" queried the expected file \"' + self.expected_file + '\" for key \"' + key + '\" which was not found. \n\t\t    Users verification code is likely incorrect (contains a typo in the key name)'
      raise RuntimeError(errstr)

    values   = getKeyValuesAsInt(output_flat,key)
    status,err = compareInteger(values,tolerance,values_e)
    kerr = ''
    if status == False:
      kerr = 'Key = \"' + key + '\" --> ' + err
    self.updateStatus(status,kerr)

  def compareLiteral(self,key):
    expected,expected_flat = self.getExpected()
    output,output_flat = self.getOutput()
    values_e = getKeyValues(expected_flat,key)
    if len(values_e) == 0:
      errstr = '[SciAth][VerificationError] Test \"' + self.name + '\" queried the expected file \"' + self.expected_file + '\" for key \"' + key + '\" which was not found. \n\t\t    Users verification code is likely incorrect (contains a typo in the key name)'
      raise RuntimeError(errstr)
    values   = getKeyValues(output_flat,key)
    status,err = compareLiteral(values,values_e)
    kerr = ''
    if status == False:
      kerr = 'Key = \"' + key + '\" --> ' + err
    self.updateStatus(status,kerr)

  def compareUnixDiff(self):
    expected,expected_flat = self.getExpected()
    output,output_flat = self.getOutput()
    status,err = compareLiteral(output,expected)
    kerr = ''
    if status == False:
      kerr = 'Key = \"' + '<entire file>' + '\" --> ' + err
    self.updateStatus(status,kerr)

  def clean(self):
    outfile = os.path.join(self.output_path,self.output_file)
    cmpfile = self.comparison_file
    print('<test> rm -f ' + outfile)
    if outfile != cmpfile and cmpfile:
      print('<test> rm -f ' + cmpfile)
