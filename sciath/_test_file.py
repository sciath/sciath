import os
import shlex

import yaml

import sciath.test
import sciath.job
import sciath.verifier
import sciath.verifier_line


def create_tests_from_file(filename):

    with open(filename, 'r') as input_file:
        data = yaml.safe_load(input_file)

    if not data:
        raise Exception("[SciATH] did not successfully read from %s" % filename)

    if not isinstance(data, list):
        raise Exception('Tests file must be a sequence')

    tests = []
    for entry in data:
        if not isinstance(entry, dict):
            raise Exception('Incorrectly formatted test entry (must be a mapping)')

        if 'name' not in entry:
            raise Exception('Each test entry must specify a name')
        if not entry['name']:
            raise Exception('Names cannot be empty')

        if 'command' in entry and 'commands' in entry:
            raise Exception('Cannot specify both command: and commands:')
        if 'command' not in entry and 'commands' not in entry:
            raise Exception('Must specify command: or commands: for each entry')
        commands_raw = entry['command'] if 'command' in entry else entry['commands']
        if isinstance(commands_raw, str):
            commands = [commands_raw]
        elif isinstance(commands_raw, list):
            commands = commands_raw
        else:
            raise Exception('command: or commands: fields must be a string or a sequence')

        commands = [_replace_here_marker(command, filename) for command in commands]

        commands = [shlex.split(command) for command in commands]  # split, respecting quotes
        for command in commands:
            if not command:
                raise Exception('Commands cannot be empty')

        expected = entry['expected']
        expected = _replace_here_marker(expected, filename)
        if not os.path.isabs(expected):
            expected = os.path.join(os.path.dirname(filename), expected)

        if len(commands) == 1:
            job = sciath.job.Job(commands[0], name=entry['name'])
        else:
            job = sciath.job.JobSequence(commands[-1], name=entry['name'])
            for i in reversed(range(len(commands)-1)):
                job.append(sciath.job.Job(commands[i]))
        test = sciath.test.Test(job, entry['name'])

        comparison_file = entry['comparison_file'] if 'comparison_file' in entry else None

        verifier_type = entry['type'] if 'type' in entry else 'text_diff'
        if verifier_type == 'text_diff':
            if 'expected' not in entry or not entry['expected']:
                raise Exception('Each test entry must defined an expected file')
            test.verifier = sciath.verifier.ComparisonVerifier(
                    test, expected, comparison_file=comparison_file)
        elif verifier_type == 'float_lines':
            if 'expected' not in entry or not entry['expected']:
                raise Exception('Each test entry must defined an expected file')
            key = entry['key'] if 'key' in entry else ''
            test.verifier = sciath.verifier_line.LineVerifier(
                    test, expected, comparison_file=comparison_file)
            test.verifier.rules.append(sciath.verifier_line.key_and_float_rule(key))
        else:
            raise Exception('[SciATH] unrecognized type %s' % verifier_type)

        tests.append(test)

    return tests


def _replace_here_marker(string, filename):
    # FIXME: this string could easily clash. It should probably be changeable from the command line.
    return string.replace('HERE', os.path.abspath(os.path.dirname(filename)))
