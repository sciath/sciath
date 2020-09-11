""" A very simple, inefficient parser for a subset of YAML files

    Generally, one would prefer to use a full-featured Python module like
    strictyaml, ruamel.yaml or PyYAML. We avoid that here because SciATH
    is intended to work out-of-the-box on as many clusters as possible.
"""

from sciath.utility import DotDict

def parse_yaml_subset_from_file(filename):  #pylint: disable=too-many-branches,too-many-locals
    """ Parse a subset of YAML files into a nested structure of list and dict objects

        All data are interpreted as strings, ignoring "#" and any trailing characters.
        Flow style is not supported, only block collections.
    """
    with open(filename, 'r') as input_file:
        lines = input_file.readlines()

    stack = []
    line_number = 0
    for line_number, line in enumerate(lines, start=1):  #pylint: disable=too-many-nested-blocks
        # Add content to nested structure
        for entry in _parse_line(line, filename, line_number):
            indent = entry.indent
            entry_type = entry.entry_type
            key = entry.key
            value = entry.value
            if not stack:
                # The first entry
                if entry_type == 's':
                    data = [value]
                    prev_key = None
                elif entry_type == 'm':
                    data = {key: value}
                    prev_key = key
                stack = [DotDict(entry_type=entry_type, indent=indent, data=data)]
            else:
                curr = stack[-1]
                if indent != curr.indent:
                    if indent > curr.indent:
                        prev = curr

                        # Create a new stack frame with an empty list or dict
                        new_data = {} if entry_type == 'm' else []
                        stack.append(DotDict(entry_type=entry_type, indent=indent, data=new_data))
                        curr = stack[-1]

                        # Insert new data as value in preceding item
                        if prev.entry_type == 's':
                            if prev.data[-1]:
                                _parse_error(
                                    filename, line_number,
                                    "Data not allowed on previous sequence line, when nesting"
                                )
                            prev.data[-1] = new_data
                        else:
                            if prev.data[prev_key]:
                                _parse_error(
                                    filename, line_number,
                                    "Data not allowed on previous mapping line, when nesting"
                                )
                            prev.data[prev_key] = new_data
                    else:
                        # Unwind the stack
                        while True:
                            stack.pop()
                            if not stack:
                                _parse_error(filename, line_number,
                                             "Invalid indentation")
                            curr = stack[-1]
                            if indent == curr.indent:
                                break

                # Add new entry to current list or dict
                if entry_type != curr.entry_type:
                    _parse_error(filename, line_number, "Invalid entry type")
                if entry_type == 's':
                    curr.data.append(value)
                    prev_key = None
                else:
                    if key in curr.data:
                        _parse_error(filename, line_number,
                                     "Duplicate key: %s" % key)
                    curr.data[key] = value
                    prev_key = key

    return stack[0].data


def _parse_error(filename, line_number, message):
    raise Exception("[SciATH] %s:%d  File parse error: %s" %
                    (filename, line_number, message))

def _compute_indent(string, filename, line_number):
    len_string_spaces_stripped = len(string.lstrip(' '))
    if  len(string.lstrip()) != len_string_spaces_stripped:
        _parse_error(filename, line_number, "Indent with spaces only")
    return len(string) - len_string_spaces_stripped

def _parse_line(line, filename, line_number):

    # Remove comments and strip trailing whitespace from content
    content = line.split('#')[0].rstrip()

    entries = []
    while content:
        indent = _compute_indent(content, filename, line_number)
        if content[indent] == '-':
            entry_type = 's'
            key = None
            if ':' in content:
                value = ''
                content = content[:indent] + ' ' + content[indent+1:]
            else:
                value = content[indent+1:].strip()
                content = None
            entries.append(DotDict(indent=indent, entry_type=entry_type, key=key, value=value))
        elif ':' in content:
            entry_type = 'm'
            key, value = content.split(':', 1)
            key = key.strip()
            value = value.strip()
            content = None
            entries.append(DotDict(indent=indent, entry_type=entry_type, key=key, value=value))
        elif content.strip():
            _parse_error(filename, line_number, 'Non-empty, non-comment lines must start with - or contain :')

    return entries
