import os


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
