import os
import pprint

import sciath._yaml_parse


filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'input.yml')
data = sciath._yaml_parse.parse_yaml_subset_from_file(filename)
pprint.PrettyPrinter(width=8192).pprint(data)
