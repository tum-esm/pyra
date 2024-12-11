import glob
import os
import time


def read_last_file_line(
    file_path: str,
    ignore_trailing_whitespace: bool = True,
) -> str:
    """Reads the last non empty line of a file"""

    with open(file_path, "rb") as f:
        f.seek(-1, os.SEEK_END)

        if ignore_trailing_whitespace:
            while f.read(1) in [b"\n", b" "]:
                try:
                    f.seek(-2, os.SEEK_CUR)
                except OSError:
                    # reached the beginning of the file
                    return ""

            f.seek(-1, os.SEEK_CUR)
            # now the cursor is right before the last
            # character that is not a newline or a space

        last_line: bytes = b""
        new_character: bytes = b""
        while True:
            new_character = f.read(1)
            if new_character == b"\n":
                break
            last_line += new_character
            f.seek(-2, os.SEEK_CUR)

        return last_line.decode().strip()[::-1]


def find_most_recent_files(directory_path: str, time_limit: int) -> list[str]:
    """Find the most recently modified files in a directory.

    Args:
        directory_path: The path to the directory to search.
        time_limit: The time limit in seconds.

    Returns:
        A list of the most recently modified files sorted by modification time
        (the most recent first) and only including files modified within the
        time limit.
    """
    current_timestamp = time.time()
    files = [f for f in glob.glob(os.path.join(directory_path, "*")) if os.path.isfile(f)]
    modification_times = [os.path.getmtime(f) for f in files]
    merged = sorted(
        [
            (f, t)
            for f, t in list(zip(files, modification_times))
            if t >= (current_timestamp - time_limit)
        ],
        key=lambda x: x[1],
        reverse=True,
    )
    return [f for f, t in merged]
