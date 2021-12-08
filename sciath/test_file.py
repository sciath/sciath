""" Logic to create SciATH Tests from a specification file """
import os
import shlex
import re
import collections

import sciath.test
import sciath.job
import sciath.task
import sciath.verifier
import sciath.verifier_line
from sciath import yaml_parse


class SciATHTestFileException(Exception):
    """ Exception for an invalid SciATH test definition file"""


def create_tests_from_file(filename):
    """ Creates a list of SciATH tests from a YAML file """
    #pylint: disable=bad-option-value,raise-missing-from
    try:
        data = yaml_parse.parse_yaml_subset_from_file(filename)
    except yaml_parse.SciATHYAMLParseException as exception:
        raise SciATHTestFileException("Error parsing file: %s" % exception)

    if not isinstance(data, dict) or 'tests' not in data or not isinstance(
            data['tests'], list):
        raise SciATHTestFileException(
            "File needs 'tests:' containing a sequence of test entries")

    replacement_map = _build_replacement_map(data, filename)

    tests = []
    for entry in data['tests']:
        if not isinstance(entry, dict):
            raise SciATHTestFileException(
                'Incorrectly formatted test entry (must be a mapping)')
        job = _create_job_from_entry(entry, replacement_map)
        test = _create_test_from_entry(job, entry, filename, replacement_map)
        tests.append(test)

    return tests


def _apply_replacement_map(string, replacement_map):
    output_string = string
    for key, value in replacement_map.items():
        output_string = output_string.replace(key, value)
    return output_string


def _build_environment_map(data):
    environment_map = {}
    if 'environment' in data:
        variable_list = data['environment']
        if not isinstance(variable_list, list):
            raise SciATHTestFileException(
                'Environment variables must be a sequence')
        for variable in variable_list:
            if not variable:
                raise SciATHTestFileException(
                    'Empty environment variables not allowed')
            if variable[0] == '$':
                variable = variable[1:]
            if not re.match(r'^\w+$', variable):
                raise SciATHTestFileException(
                    'Environment variable name not well-formed: %s' % variable)
            value = os.getenv(variable)
            if value is None:
                raise SciATHTestFileException(
                    'Expected environment variable %s not defined.' % variable)
            environment_map['$' + variable] = value
    environment_map = collections.OrderedDict(
        sorted(environment_map.items(), reverse=True))
    return environment_map


def _build_replacement_map(data, filename, here_marker='HERE'):
    replacement_map = _build_environment_map(data)
    replacement_map[here_marker] = os.path.abspath(os.path.dirname(filename))
    return replacement_map


def _create_job_from_entry(entry, replacement_map):
    if "name" not in entry:
        raise SciATHTestFileException("Each test entry must specify a name")
    if not entry["name"]:
        raise SciATHTestFileException("Names cannot be empty")

    taskinfo_names = ("command", "commands", "task", "tasks")
    taskinfo_found = False
    for name in taskinfo_names:
        if name in entry:
            if taskinfo_found:
                raise SciATHTestFileException(
                    "Each test can only specify one of %s" % taskinfo_names)
            taskinfo = entry[name]
            taskinfo_found = True
    if not taskinfo_found:
        raise SciATHTestFileException(
            "Tasks or commands must be defined for each test")

    if isinstance(taskinfo, str):
        taskinfo = [taskinfo]
    elif not isinstance(taskinfo, list):
        raise SciATHTestFileException(
            "Task or command entries must be a string or a sequence")

    time_job = _get_time_from_entry(entry)
    ranks_job = int(entry["ranks"]) if "ranks" in entry else None

    tasks = []
    for info_entry in taskinfo:
        if isinstance(info_entry, str):
            info_entry = {"command": info_entry}
        tasks.append(
            _create_task_from_entry(info_entry,
                                    ranks_default=ranks_job,
                                    replacement_map=replacement_map))

    job = sciath.job.Job(tasks, name=entry["name"], minimum_wall_time=time_job)
    return job


def _create_task_from_entry(entry, ranks_default, replacement_map):
    if "command" not in entry:
        raise SciATHTestFileException("Tasks must specify a command")
    command = shlex.split(
        _apply_replacement_map(entry["command"], replacement_map))
    ranks = int(entry["ranks"]) if "ranks" in entry else ranks_default
    if ranks is None:
        ranks = 0
    return sciath.task.Task(command, ranks=ranks)


def _create_test_from_entry(job, entry, filename, replacement_map):
    test = sciath.test.Test(job)
    _populate_verifier_from_entry(test, entry, filename, replacement_map)
    _populate_groups_from_entry(test, entry)
    return test


def _get_time_from_entry(entry):
    time = None
    if 'time' in entry:
        if 'walltime' in entry:
            raise SciATHTestFileException(
                'Entry cannot specify both time and walltime')
        time = float(entry['time'])
    if 'walltime' in entry:
        time = float(entry['walltime'])
    if time is not None and time <= 0:
        time = None
    return time


def _populate_groups_from_entry(test, entry):
    if 'group' in entry and 'groups' in entry:
        raise SciATHTestFileException('Cannot specify both group: and groups:')
    if 'group' in entry or 'groups' in entry:
        groups_raw = entry['group'] if 'group' in entry else entry['groups']
        if isinstance(groups_raw, str):
            groups_list = [groups_raw]
        elif isinstance(groups_raw, list):
            groups_list = groups_raw
        else:
            raise SciATHTestFileException(
                'Group: or groups: fields must be a string or a sequence')
        for group in groups_list:
            test.add_group(group)


def _populate_verifier_from_entry(test, entry, filename, replacement_map):
    verifier_type = entry['type'] if 'type' in entry else 'text_diff'

    if verifier_type == 'exit_code':
        test.verifier = sciath.verifier.ExitCodeVerifier(test)
        return

    comparison_file = entry['comparison'] if 'comparison' in entry else None

    # All subsequent verifiers use an expected file
    if 'expected' not in entry or not entry['expected']:
        raise SciATHTestFileException(
            'Each test entry must defined an expected file')
    expected = entry['expected']
    expected = _apply_replacement_map(expected, replacement_map)
    if not os.path.isabs(expected):
        expected = os.path.join(os.path.dirname(filename), expected)

    if verifier_type == 'text_diff':
        test.verifier = sciath.verifier.ComparisonVerifier(
            test, expected, comparison_file=comparison_file)
    elif verifier_type == 'float_lines':
        test.verifier = sciath.verifier_line.LineVerifier(
            test, expected, comparison_file=comparison_file)
        if 'rules' not in entry:
            raise SciATHTestFileException('rules: expected')
        rules = entry['rules']
        if not isinstance(rules, list):
            raise SciATHTestFileException('rules: should contain a sequence')
        for rule in rules:
            if not isinstance(rule, dict):
                raise SciATHTestFileException('Each rule should be a mapping')
            if 'key' not in rule:
                raise SciATHTestFileException('Each rule should have a key:')
            key = rule['key']
            rtol_string = rule.get('rtol', None)
            atol_string = rule.get('atol', None)
            rtol = float(rtol_string) if rtol_string else None
            atol = float(atol_string) if atol_string else None
            rule_func = sciath.verifier_line.key_and_float_rule(key,
                                                                rel_tol=rtol,
                                                                abs_tol=atol)
            test.verifier.rules.append(rule_func)
    else:
        raise SciATHTestFileException('Unrecognized verifier type %s' %
                                      verifier_type)
