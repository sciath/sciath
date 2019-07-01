#!/usr/bin/env sh
printf "datum 3e1\n"
printf "datum 3e10\n"
printf "datum 3e-10\n"
printf "datum 1234.56\n"
printf "datum 12345600000\n"

# A value which, in the context of the application, is very close to zero,
# hence can cause a relative test to fail when comparing to another
# value, also very close to zero
printf "datum 3.0e-24\n"
