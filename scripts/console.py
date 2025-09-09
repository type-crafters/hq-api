log = lambda string, end="\n", sep=" ": print(f"\033[90m{string}\033[0m", end="\n", sep=" ")
info = lambda string, end="\n", sep=" ": print(f"\033[36m{string}\033[0m", end="\n", sep=" ")
warn = lambda string, end="\n", sep=" ": print(f"\033[31m{string}\033[0m", end="\n", sep=" ")
error = lambda string, end="\n", sep=" ": print(f"\033[31m{string}\033[0m", end="\n", sep=" ")