

import numpy as np
import math as math
import re

def compareLiteral(input,expected):
  print(len(input))
  
  if len(input) != len(expected):
    print("<compareLiteral failed>: input and expected are of different length");
    print("  expected:",expected)
    print("  input:   ",input)
  
  for index in range(0,len(expected)):
    if input[index] != expected[index]:
      print("<compareLiteral failed>")
      print("  expected:",expected)
      print("  input:   ",input)
      print("  index[" + str(index) +  "]" + " input" ,  input[index] , ": expected " , expected[index]);

def compareFloatingPoint(input,tolerance,expected):
  if len(input) != len(expected):
    print("<compareFloatingPoint failed>: input and expected are of different length");
    print("  expected:",e_f)
    print("  input:   ",i_f)
  
  tmp = np.array(input)
  i_f = tmp.astype(np.float)
  tmp = np.array(expected)
  e_f = tmp.astype(np.float)
  tol_f = float(tolerance)
  
  for index in range(0,len(e_f)):
    absdiff = np.abs(i_f[index] - e_f[index]);
    if absdiff > tol_f:
      print("<compareFloatingPoint failed>: tolerance " + str(tol_f), "not satisifed")
      print("  expected:",e_f)
      print("  input:   ",i_f)
      print("  index[" + str(index) + "]" + " input" ,  i_f[index] , ": expected " , e_f[index], "(+/-"+str(tol_f)+")"  )

def compareInteger(input,tolerance,expected):
  if len(input) != len(expected):
    print("<compareInteger failed>: input and expected are of different length");
    print("  expected:",e_i)
    print("  input:   ",i_i)
  
  tmp = np.array(input)
  i_i = tmp.astype(np.int)
  tmp = np.array(expected)
  e_i = tmp.astype(np.int)
  tol_i = int(tolerance)
  
  for index in range(0,len(e_i)):
    absdiff = np.abs(i_i[index] - e_i[index]);
    if absdiff > tol_i:
      print("<compareInteger failed>: tolerance " + str(tol_i), "not satisifed")
      print("  expected:",e_i)
      print("  input:   ",i_i)
      print("  index[" + str(index) + "]" + " input" ,  i_i[index] , ": expected " , e_i[index] , "(+/-"+str(tol_i)+")" )


def parseFile(filename,keywords):
  file = open(filename,"r")

  contents = []
  for line in file:
    if line.rstrip():
      if not any(keywords in line for keywords in keywords):
        stripped_line = line.rstrip()
        contents.append(stripped_line)
        #s2 = stripped_line.rstrip()
        #splitter = s2.split(' ')
        #contents.append(splitter)

  file.close()
  return contents

# look for a line starting with keyword
# check for open bracket
# if found, scan for closing bracket and parse everything found
def getKeyValues(contents,keyword):
  removewords = [ keyword, '=', ';' ]
  
  c1 = contents.replace('\n',' ') # should store this mess rather than re-apply it upon each query

  filtered = re.findall("^" + keyword + "\s*=\s*[\[\(\{](.*?)[\}\)\]]", c1)

  flattened = []
  for sublist in filtered:
    sublist = sublist.replace(',','')
    ss = sublist.split(' ')
    
    for val in ss:
      if val != '':
        flattened.append(val)

  return flattened


def getKeyValuesAsInt(contents,keyword):
  result = getKeyValues(contents,keyword)
  tmp = np.array(result)
  values = tmp.astype(np.int)
  return values

def getKeyValuesAsFloat(contents,keyword):
  result = getKeyValues(contents,keyword)
  tmp = np.array(result)
  values = tmp.astype(np.float)
  return values



contents = parseFile('test.std',['!'])
for row in contents:
  print(row)


c1 = 'verify  =  { 3.3     \n 4.4 }'
c1 = c1 + ' xverify {5.5 , 6.6 }'

result = getKeyValues(c1,'verify')
print('res = ',result)

flist = getKeyValuesAsFloat(c1,'verify')
print(flist)


print("--------------")

s = '  verify {\n 3.3, \n 4.4 }'
print(s)
a = s[s.find("{")+1:s.find("}")]
print(a)


print('test 2')
s = 'verify    { 3.3 \n 4.4 }'
s = s + ' xverify {5.5 , 6.6 }'
print(s)

s = s.replace('\n',' ')
#s = s.replace(',',' ')
print(s)

#x = re.findall("\{.*?\}", s)
#x = re.findall("\{(.*?)\}", s)
#x = re.findall("[\{\[].*?[\]\}]", s)
#x = re.findall("[\[\(\{](.*?)[\}\)\]]", s)
x = re.findall("^verify\s*[\[\(\{](.*?)[\}\)\]]", s)
print('x',x)

flattened = []
for sublist in x:
  sublist = sublist.replace(',','')
  ss = sublist.split(' ')
  
  for val in ss:
    if val != '':
      flattened.append(val)

print(flattened)
#tmp = np.array(x)
#print(tmp.astype(np.float))



