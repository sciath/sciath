""" Logic to create SciATH Tests from a specification file """
import os
import shlex

import sciath.test
import sciath.job
import sciath.task
import sciath.verifier
import sciath.verifier_line
from sciath import yaml_parse


def create_tests_from_file(filename):
    """ Creates a list of SciATH tests from a YAML file """
    data = yaml_parse.parse_yaml_subset_from_file(filename)

    if not data:
        raise Exception("[SciATH] did not successfully read from %s" % filename)

    if not isinstance(data, dict) or 'tests' not in data or not isinstance(data['tests'], list):
        raise Exception("[SciATH] file needs 'tests:' containing a sequence of test entries")

    tests = []
    for entry in data['tests']:
        if not isinstance(entry, dict):
            raise Exception('Incorrectly formatted test entry (must be a mapping)')
        job = _create_job_from_entry(entry, filename)
        test = _create_test_from_entry(job, entry, filename)
        tests.append(test)

    return tests


def _create_job_from_entry(entry, filename):
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

    ranks = int(entry['ranks']) if 'ranks' in entry else 1

    tasks = [sciath.task.Task(command, ranks=ranks) for command in commands]
    job = sciath.job.Job(tasks, name=entry['name'])
    return job


def _create_test_from_entry(job, entry, filename):
    test = sciath.test.Test(job)
    _populate_verifier_from_entry(test, entry, filename)
    _populate_groups_from_entry(test, entry)
    return test


def _populate_groups_from_entry(test, entry):
    if 'group' in entry and 'groups' in entry:
        raise Exception('[SciATH] Cannot specify both group: and groups:')
    if 'group' in entry or 'groups' in entry:
        groups_raw = entry['group'] if 'group' in entry else entry['groups']
        if isinstance(groups_raw, str):
            groups_list = [groups_raw]
        elif isinstance(groups_raw, list):
            groups_list = groups_raw
        else:
            raise Exception('group: or groups: fields must be a string or a sequence')
        for group in groups_list:
            test.add_group(group)

def _populate_verifier_from_entry(test, entry, filename):
    expected = entry['expected']
    expected = _replace_here_marker(expected, filename)
    if not os.path.isabs(expected):
        expected = os.path.join(os.path.dirname(filename), expected)

    comparison_file = entry['comparison'] if 'comparison' in entry else None

    verifier_type = entry['type'] if 'type' in entry else 'text_diff'
    if verifier_type == 'text_diff':
        if 'expected' not in entry or not entry['expected']:
            raise Exception('Each test entry must defined an expected file')
        test.verifier = sciath.verifier.ComparisonVerifier(
            test, expected, comparison_file=comparison_file)
    elif verifier_type == 'float_lines':
        if 'expected' not in entry or not entry['expected']:
            raise Exception('Each test entry must defined an expected file')
        test.verifier = sciath.verifier_line.LineVerifier(
            test, expected, comparison_file=comparison_file)
        if 'rules' not in entry:
            raise Exception('rules: expected')
        rules = entry['rules']
        if not isinstance(rules, list):
            raise Exception('rules: should contain a sequence')
        for rule in rules:
            if not isinstance(rule, dict):
                raise Exception('Each rule should be a mapping')
            if 'key' not in rule:
                raise Exception('Each rule should have a key:')
            key = rule['key']
            rtol_string = rule.get('rtol', None)
            atol_string = rule.get('atol', None)
            rtol = float(rtol_string) if rtol_string else None
            atol = float(atol_string) if atol_string else None
            rule_func = sciath.verifier_line.key_and_float_rule(
                key, rel_tol=rtol, abs_tol=atol)
            test.verifier.rules.append(rule_func)
    else:
        raise Exception('[SciATH] unrecognized type %s' % verifier_type)

def _replace_here_marker(string, filename, marker='HERE'):
    return string.replace(marker, os.path.abspath(os.path.dirname(filename)))