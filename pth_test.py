

import numpy as np
import math as math
import re

def compareLiteral(input,expected):
  status = True
  err = ''
  
  if len(input) != len(expected):
    status = False
    err = err + "compareLiteral [failed]\nReason: input and expected are of different length\n"
    err = err + ("  expected: %s\n" % expected)
    err = err + ("  input:    %s\n" % input)
    return status,err

  for index in range(0,len(expected)):
    if input[index] != expected[index]:
      status = False
      err = err + "compareLiteral [failed]\nReason: strings are different\n"
      err = err + ("  expected: %s\n" % expected)
      err = err + ("  input:    %s\n" % input)
      err = err + "  index[" + str(index) +  "]" + " input \"" +  input[index] + "\" != expected \"" + expected[index] + "\"\n"

  return status,err

def compareFloatingPoint(input,tolerance,expected):
  status = True
  err = ''

  tmp = np.array(input)
  i_f = tmp.astype(np.float)
  tmp = np.array(expected)
  e_f = tmp.astype(np.float)
  tol_f = float(tolerance)

  if len(input) != len(expected):
    status = False
    err = err + "compareFloatingPoint [failed]\nReason: input and expected are of different length\n"
    err = err + ("  expected: %s\n" % e_f)
    err = err + ("  input:    %s\n" % i_f)
    return status,err

  for index in range(0,len(e_f)):
    absdiff = np.abs(i_f[index] - e_f[index]);
    if absdiff > tol_f:
      status = False
      err = err + "compareFloatingPoint [failed]\nReason: tolerance " + str(tol_f) + " not satisifed\n"
      err = err + ("  expected: %s\n" % e_f)
      err = err + ("  input:    %s\n" % i_f)
      err = err + "  index[" + str(index) + "]" + (" input \"%s\"" %  i_f[index])  + (" != expected \"%s\"" % e_f[index]) + " (+/-"+str(tol_f)+")\n"

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
    status = False
    err = err + "compareInteger [failed]\nReason: input and expected are of different length\n"
    err = err + ("  expected: %s\n" % e_i)
    err = err + ("  input:    %s\n" % i_i)
    return status,err
  
  for index in range(0,len(e_i)):
    absdiff = np.abs(i_i[index] - e_i[index]);
    if absdiff > tol_i:
      status = False
      err = err + "compareInteger [failed]\nReason: tolerance " + str(tol_i) + " not satisifed\n"
      err = err + ("  expected: %s\n" % e_i)
      err = err + ("  input:    %s\n" % i_i)
      err = err + "  index[" + str(index) + "]" + (" input \"%s\"" %  i_i[index]) + (" != expected \"%s\"" % e_i[index]) + " (+/-"+str(tol_i)+")\n"

  return status,err


def parseFile(filename,keywords):
  print('Parsing file: ',filename)
  file = open(filename,"r")

  flat = ''
  contents = []
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

  f1 = re.findall("\s*" + keyword + "\s*=\s*[\[\(\{](.*?)[\}\)\]]", c1)
  f2 = re.findall("\s*" + keyword + "\s+[\[\(\{](.*?)[\}\)\]]", c1)

  f3 = re.findall("\s*" + keyword + "\s*=\s*([0-9a-zA-Z-\_\.]*)", c1)
  f4 = re.findall("\s*" + keyword + "\s+([0-9a-zA-Z-\_\.]*)", c1)

  filtered = []
  if f1:
    for item in f1:
      if item != '':
        trimmed = item.lstrip()
        trimmed = trimmed.rstrip()
        filtered.append(trimmed)
  if f2:
    for item in f2:
      if item != '':
        trimmed = item.lstrip()
        trimmed = trimmed.rstrip()
        filtered.append(trimmed)
  if f3:
    for item in f3:
      if item != '':
        trimmed = item.lstrip()
        trimmed = trimmed.rstrip()
        filtered.append(trimmed)
  if f4:
    for item in f4:
      if item != '':
        trimmed = item.lstrip()
        trimmed = trimmed.rstrip()
        filtered.append(trimmed)

  return filtered


def getKeyValuesAsInt(contents,keyword):
  result = getKeyValues(contents,keyword)

  flattened = []
  for sublist in result:

    for val in sublist:
      if val != '':
        val = val.replace(',','')
        ss = val.split(' ')
        for num in ss:
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
    val = r.split(' ')
    for v in val:
      if v != '':
        flattened.append(v)

  #print('flattened = ',flattened)
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

def test1():
  (contents,flatcontents) = parseFile('test.std',['!'])
  print('File')
  for row in contents:
    print(row)

  #print(flatcontents)
  key = '\$verify'

  values = getKeyValues(flatcontents,key)
  print('values')
  print(values)

  values = getKeyValuesAsFloat(flatcontents,key)
  print(values)

def test2():
  (contents,flatcontents) = parseFile('test03c.expected',['!'])
  
  #print(flatcontents)
  key = 'KSP Residual norm'
  
  values = getKeyValues(flatcontents,key)
  print('values')
  print(values)
  
  values = getKeyValuesAsFloat(flatcontents,key)
  print(values)

  key = 'dt_courant ='
  values = getKeyValues(flatcontents,key)
  print('values')
  print(values)

  values = getKeyValuesNLinesInclusive(contents,'_DataExCompleteCommunicationMap',8)
  print(values)
  values = getKeyValuesNLinesExclusive(contents,'_DataExCompleteCommunicationMap',7)
  print(values)

def test3():
  (contents,flatcontents) = parseFile('test03c.expected',['!'])
  
  expected = getKeyValuesNLinesExclusive(contents,'_DataExCompleteCommunicationMap',7)
  output = getKeyValuesNLinesExclusive(contents,'_DataExCompleteCommunicationMap',7)
  output[2] = 'aaa'
  status,err = compareLiteral(output,expected)
  print(err)

  status,err = compareFloatingPoint([4.4,3.3],0.01,[4.4,3.4])
  print(err)

  status,err = compareInteger(['4','3'],'2',['3'])
  print(err)

class bcolors:
  HEADER = '\033[95m'
  OKBLUE = '\033[94m'
  OKGREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  ENDC = '\033[0m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'

class UnitTest:
  
  def __init__(self, name,ranks,execute,expected_file):
    self.passed = -1
    self.walltime = "00:05:00"
    self.errormessage = ''
    self.name = name
    self.ranks = ranks
    self.execute = execute
    self.expected_file = expected_file
    self.keywords = [ '#', '!', '//' ]
    self.output_file = name + '-p' + str(ranks) + '.output'


  def verify(self,a):
    a = 0


  def setVerifyMethod(self,verify):
    self.verify = verify


  def appendKeywords(self,keywords):
    self.keywords.append(keywords)
  #print(self.keywords)


  def verifyOutput(self):
    (self.expected_contents,self.expected_flatcontents) = parseFile(self.expected_file,self.keywords)
    (self.output_contents,self.output_flatcontents) = parseFile(self.output_file,self.keywords)
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
      
      if self.passed == False:
        print(bcolors.FAIL,' [' + self.name + ']   *** FAILED *** ' + bcolors.ENDC)
      else:
        print(bcolors.OKGREEN,' [' + self.name + ']   passed ' + bcolors.ENDC)

    if type == 'log':
      if self.passed == False:
        #        print(bcolors.FAIL + '_______________________________________________\n' + '[' + self.name + '] reason for failure\n' + self.errormessage + ' ' + bcolors.ENDC)
        print(bcolors.FAIL +  '[' + self.name + '] reason for failure\n' + '--------------------------------------------------------------\n' + self.errormessage + ' ' + bcolors.ENDC)


  def compareFloatingPoint(self,key,tolerance):
    expected,expected_flat = self.getExpected()
    output,output_flat = self.getOutput()
    values_e = getKeyValuesAsFloat(expected_flat,key)
    values   = getKeyValuesAsFloat(output_flat,key)
    status,err = compareFloatingPoint(values,tolerance,values_e)
    kerr = 'Key = \"' + key + '\" --> ' + err
    self.updateStatus(status,kerr)


  def compareInteger(self,key,tolerance):
    expected,expected_flat = self.getExpected()
    output,output_flat = self.getOutput()
    values_e = getKeyValuesAsInt(expected_flat,key)
    values   = getKeyValuesAsInt(output_flat,key)
    status,err = compareInteger(values,tolerance,values_e)
    kerr = 'Key = \"' + key + '\" --> ' + err
    self.updateStatus(status,kerr)

  def compareLiteral(self,key):
    expected,expected_flat = self.getExpected()
    output,output_flat = self.getOutput()
    values_e = getKeyValues(expected_flat,key)
    values   = getKeyValues(output_flat,key)
    status,err = compareLiteral(values,values_e)
    kerr = 'Key = \"' + key + '\" --> ' + err
    self.updateStatus(status,kerr)


def test1_example():

  ranks = 1

  launch = './ex1 -options_file a'
  
  expected_file = 'ex1.expected'
  
  def comparefunc(unittest):
    expected,expected_flat = unittest.getExpected()
    output,output_flat = unittest.getOutput()

    key = '\$cputime'
    values_e = getKeyValuesAsFloat(expected_flat,key)
    values   = getKeyValuesAsFloat(output_flat,key)
    status,err = compareFloatingPoint(values,0.01,values_e)
    unittest.updateStatus(status,err)

    key = '\$residuals'
    values_e = getKeyValuesAsFloat(expected_flat,key)
    values   = getKeyValuesAsFloat(output_flat,key)
    status,err = compareFloatingPoint(values,0.000001,values_e)
    unittest.updateStatus(status,err)

    key = '\$kspits'
    values_e = getKeyValuesAsInt(expected_flat,key)
    values   = getKeyValuesAsInt(output_flat,key)
    status,err = compareFloatingPoint(values,0,values_e)
    unittest.updateStatus(status,err)

    key = '\$norm'
    values_e = getKeyValuesAsFloat(expected_flat,key)
    values   = getKeyValuesAsFloat(output_flat,key)
    status,err = compareFloatingPoint(values,0.01,values_e)
    unittest.updateStatus(status,err)

    key = '\$rms'
    values_e = getKeyValuesAsFloat(expected_flat,key)
    values   = getKeyValuesAsFloat(output_flat,key)
    status,err = compareFloatingPoint(values,0.01,values_e)
    unittest.updateStatus(status,err)

  # Create unit test object
  ex1 = UnitTest('ex1',ranks,launch,expected_file)
  ex1.setVerifyMethod(comparefunc)
  ex1.appendKeywords('@')

  return(ex1)

def run_my_tests():
  registered_tests = [test1_example(), test1_example(), test1_example(), test1_example()]

  for test in registered_tests:
    print('** This is a place-holder for an actual job launcher **')
    print('  <no batch> will just execute ' + test.execute)

    test.verifyOutput()

  print('-- Unit test report summary --')
  for test in registered_tests:
    test.report('summary')

  print('-- Unit test error messages --')
  for test in registered_tests:
    test.report('log')


if __name__ == "__main__":
  #test1()
  #test2()
  #test3()
  #test1_example()
  run_my_tests()
