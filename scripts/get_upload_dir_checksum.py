import sys
import os
import json
import hashlib

assert len(sys.argv) == 2, 'call this script with "python <scriptname> <directoryname>"'
assert sys.version.startswith("3.10"), "script requires Python 3.10"

# check whether upload directory and meta file exist
upload_directory = sys.argv[1]
upload_meta_path = os.path.join(upload_directory, "upload-meta.json")
assert os.path.isdir(upload_directory), f'"{upload_directory}" is not a directory'
assert os.path.isfile(upload_meta_path), f'"{upload_meta_path}" is not a file'

# get and validate fileList
with open(upload_meta_path) as f:
    upload_meta = json.load(f)
file_list = upload_meta["fileList"]
assert isinstance(file_list, list), f"upload_meta.fileList is not a list"

# calculate checksum over all files (sorted)
hasher = hashlib.md5()
for filename in sorted(file_list):
    filepath = os.path.join(upload_directory, filename)
    with open(filepath, "rb") as f:
        hasher.update(f.read())

# output hashsum - with a status code of 0 the programs
# stdout is a checksum, otherwise it is a traceback
print(hasher.hexdigest())
