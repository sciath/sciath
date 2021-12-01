""" Execute the sciath module as a script """
from sciath import harness


def _main():
    harness.Harness().run_from_args()


if __name__ == '__main__':
    _main()
