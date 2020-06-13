#!/usr/bin/env sh
# Additional arguments (e.g. --update) are passed through

python -m sciath  # prompt to generate configuration file, if missing
./minisciath/minisciath.py --exclude-group mpi_verify tests.yml $@

printf "You should run additional tests to verify MPI tests. Wait until any queued jobs are completed, and then run\n"
printf "  ./minisciath/minisciath.py --only-group mpi_verify tests.yml\n"
