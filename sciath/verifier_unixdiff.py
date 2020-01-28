import os
import sys
if os.name == 'posix' and sys.version_info[0] < 3:
    import subprocess32 as subprocess # To be removed once Python 2 is fully abandoned
else:
    import subprocess

from sciath.job import Job
from sciath.job import JobSequence
from sciath.job import JobDAG
from sciath.verifier import Verifier
from sciath import sciath_test_status
from sciath._io import _remove_file


class VerifierUnixDiff(Verifier):
    def __init__(self,test,expected_file,output_file=None):
      Verifier.__init__(self,test)
      if expected_file is None:
          raise RuntimeError('[Sciath] Must set expected_file on test')
      self.expected_file = expected_file
      if output_file is None:
          self.output_file = self.o_name[-1]

    def execute(self,output_path,exec_path = None):

        status = None
        report = []

        if not os.path.isfile(self.expected_file) :
            report.append("[UnixDiff] Expected file \"" + self.expected_file + "\" was not found")
            status = sciath_test_status.expected_file_not_found
            return

        output_full_path = os.path.join(output_path,self.output_file)
        if not os.path.isfile(output_full_path) :
            report.append("[UnixDiff] Output file \"" + output_full_path + "\" was not found")
            status = sciath_test_status.output_file_not_found
            return

        stdoutfile = os.path.join(output_path,"sciath.verifier-unixdiff.stdout")
        file_o = open( stdoutfile, 'w')
        ctx = subprocess.run(['diff',self.expected_file,output_full_path],stdout=file_o,stderr=subprocess.PIPE)
        e = ctx.returncode
        file_o.close()

        if int(e) != 0:
            with open(stdoutfile, 'r') as f:
                data = f.readlines()
            report += data
            for k in range(0,len(report)):
                line = report[k]
                report[k] = line.rstrip("\n")

            report.append("[UnixDiff] Expected and output files are not identical")
            report.append("[UnixDiff] Expected file: \"" + self.expected_file + "\"")
            report.append("[UnixDiff] Output file  : \"" + self.output_file + "\"")
            status = sciath_test_status.not_ok
        else:
            status = sciath_test_status.ok

        _remove_file(stdoutfile)

        return status,report
