#!/usr/bin/env sh
# Additional arguments (e.g. --update) are passed through

python -m sciath  # prompt to generate configuration file, if missing
./minisciath/minisciath.py tests.yml $@
