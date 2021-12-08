""" Execute the sciath module as a script """

import sys

from sciath import harness


def _main():
    exit_code = harness.Harness().run_from_args()
    sys.exit(exit_code)


if __name__ == '__main__':
    _main()
