import hashlib
import os
import pathlib
import sys

assert len(sys.argv) == 2, 'call this script with "python <scriptname> <directoryname>"'
assert sys.version.startswith("3.10"), "script requires Python 3.10"

# check whether upload directory and meta file exist
upload_directory = sys.argv[1].rstrip("/")
assert os.path.isdir(upload_directory), f'"{upload_directory}" is not a directory'
date_string = upload_directory.split("/")[-1]


ifg_files: list[str] = []
for p in pathlib.Path(upload_directory).glob(f"*{date_string}*"):
    if p.is_file():
        ifg_files.append(str(p))


# calculate checksum over all files (sorted)
hasher = hashlib.md5()
for filename in sorted(ifg_files):
    filepath = os.path.join(upload_directory, filename)
    with open(filepath, "rb") as f:
        hasher.update(f.read())

# output hashsum - with a status code of 0 the programs
# stdout is a checksum, otherwise it is a traceback
print(hasher.hexdigest())
