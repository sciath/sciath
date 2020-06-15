""" A very simple, inefficient parser for a subset of YAML files

    Generally, one would prefer to use a full-featured Python module like
    strictyaml, ruamel.yaml or PyYAML.
"""


def parse_yaml_subset_from_file(filename):
    """ Parse a subset of YAML files into a nested structure of list and dict objects

        All data are interpreted as strings, ignoring "#" and any trailing characters.
        Flow style is not supported, only block collections.
    """
    with open(filename, 'r') as input_file:
        lines = input_file.readlines()

    class _StackFrame():

        def __init__(self, entry_type, indent, data):
            self.entry_type = entry_type
            self.indent = indent
            self.data = data

    stack = []

    line_number = 0
    for line_number, line in enumerate(lines, start=1):

        indent, content = _parse_line(line, filename, line_number)
        if not content:
            continue

        # Parse content
        if content.startswith('-'):
            entry_type = 's'
            value = content[1:].strip()
        else:
            entry_type = 'm'
            key, value = content.split(':')
            key = key.strip()
            value = value.strip()

        # Add content to nested structure
        if not stack:
            # The first entry
            if entry_type == 's':
                data = [value]
                prev_key = None
            elif entry_type == 'm':
                data = {key: value}
                prev_key = key
            stack = [_StackFrame(entry_type, indent, data)]
        else:
            curr = stack[-1]
            if indent != curr.indent:
                if indent > curr.indent:
                    prev = curr

                    # Create a new stack frame with an empty list or dict
                    new_data = {} if entry_type == 'm' else []
                    stack.append(_StackFrame(entry_type, indent, new_data))
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


def _parse_line(line, filename, line_number):

    # Determine indentation level
    line_without_newline = line.rstrip('\n')
    content = line_without_newline.lstrip()
    indent = len(line_without_newline) - len(content)
    if line_without_newline[:indent] != ' ' * indent:
        _parse_error(filename, line_number, "Indent with spaces only")

    # Remove comments from content
    content = content.split('#')[0].rstrip()

    return indent, content


def _parse_error(filename, line_number, message):
    raise Exception("[SciATH] %s:%d  File parse error: %s" %
                    (filename, line_number, message))
