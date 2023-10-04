import os


def read_last_file_line(file_path: str) -> str:
    """Reads the last non empty line of a file"""

    with open(file_path, "rb") as f:
        try:
            f.seek(-64, os.SEEK_END)
            while True:
                currently_last_block = f.read(64).strip(b"\n ")
                f.seek(-128, os.SEEK_CUR)
                if len(currently_last_block) > 0:
                    break
            while b'\n' not in f.read(64):
                f.seek(-128, os.SEEK_CUR)
        except OSError:
            # catch OSError in case of a one line file
            f.seek(0)
        return f.read().decode().strip("\n").split("\n")[-1]
