
import os
from sciath.job import Job
from sciath.job import JobSequence
from sciath.job import JobDAG
from sciath.verifier import Verifier
from sciath import sciath_test_status
import sciath._subprocess as subp
from sciath.launcher import _removeFile


class VerifierUnixDiff(Verifier):
    def __init__(self,test,expected_file,output_file=None,**kwargs):
      Verifier.__init__(self,test,**kwargs)
      if expected_file is None:
          raise RuntimeError('[Sciath] Must set expected_file on test')
      self.expected_file = expected_file
      if output_file is None:
          self.output_file = self.o_name[-1]

    def execute(self,output_path,exec_path = None):
    
        self.status = None
        self.report = []
    
        if not os.path.isfile(self.expected_file) :
            self.report.append("[UnixDiff] Expected file \"" + self.expected_file + "\" was not found")
            self.status = sciath_test_status.expected_file_not_found
            return
   
        output_full_path = os.path.join(output_path,self.output_file)
        if not os.path.isfile(output_full_path) :
            self.report.append("[UnixDiff] Output file \"" + output_full_path + "\" was not found")
            self.status = sciath_test_status.output_file_not_found
            return
    
    
        stdoutfile = os.path.join(output_path,"sciath.verifier-unixdiff.stdout")
        file_o = open( stdoutfile, 'w')
        e = subp.run(['diff','-c',self.expected_file,self.output_file],file_o,None)
        file_o.close()
    
        if int(e) != 0:
            with open(stdoutfile, 'r') as f:
                data = f.readlines()
            self.report += data
            for k in range(0,len(self.report)):
                line = self.report[k]
                self.report[k] = line.rstrip("\n")
      
            self.report.append("[UnixDiff] Expected and output files are not identical")
            self.report.append("[UnixDiff] Expected file: \"" + self.expected_file + "\"")
            self.report.append("[UnixDiff] Output file  : \"" + self.output_file + "\"")
            self.status = sciath_test_status.not_ok
        else:
            self.status = sciath_test_status.ok
    
        _removeFile(stdoutfile)

        return


