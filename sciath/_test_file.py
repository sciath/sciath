import os
import shlex

import yaml

import sciath.test
import sciath.job
import sciath.verifier_unixdiff
import sciath.verifier_line

def create_tests_from_file(filename):

    with open(filename, 'r') as input_file:
        data = yaml.safe_load(input_file)

    if not data:
        raise Exception("[SciATH] did not successfully read from %s" % filename)

    tests = []
    for entry in data:
        if not isinstance(entry, dict):
            raise Exception('Incorrectly formatted test entry (must be a mapping)')

        if 'command' not in entry:
            raise Exception('Each test entry must specify a command')
        if not entry['command']:
            raise Exception('Commands cannot be empty')
        if 'name' not in entry:
            raise Exception('Each test entry must specify a name')
        if not entry['name']:
            raise Exception('Names cannot be empty')

        command = shlex.split(entry['command'])
        expected = entry['expected']
        if not os.path.isabs(expected):
            expected = os.path.join(os.path.dirname(filename), expected)

        test = sciath.test.Test(sciath.job.Job(command, entry['name']))

        verifier_type = entry['type'] if 'type' in entry else 'text_diff'
        if verifier_type == 'text_diff':
            if 'expected' not in entry or not entry['expected']:
                raise Exception('Each test entry must defined an expected file')
            test.verifier = sciath.verifier_unixdiff.VerifierUnixDiff(test, expected)
        elif verifier_type == 'float_lines':
            if 'expected' not in entry or not entry['expected']:
                raise Exception('Each test entry must defined an expected file')
            key = entry['key'] if 'key' in entry else ''
            test.verifier = sciath.verifier_line.VerifierLine(test, expected)
            test.verifier.rules.append(sciath.verifier_line.key_and_float_rule(key))
        else:
            raise Exception('[SciATH] unrecognized type %s' % verifier_type)

        tests.append(test)

    return tests
