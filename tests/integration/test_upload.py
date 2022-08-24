from ..fixtures import original_config, populated_upload_test_directories

# TODO: in headless-upload mode, do not loop infinitely
# TODO: test without removal (+ rerunning)
# TODO: test with removal

# 1. Before upload, create a dst dir that does not
#    exist on the remote dir
# 2. After upload, download dst dir and compare to
#    original dir using the "diff" command


def test_upload(original_config, populated_upload_test_directories) -> None:
    upload_config = original_config["upload"]
    # TODO: add correct settings to config and write config
    # TODO: calculate checksum locally

    # TODO: trigger headless upload process

    # TODO: Assert existence of checksum script on remote
    # TODO: calculate checksum on remote
    # TODO: calculate checksum locally (a second time)

    # TODO: Assert equality of all three checksums
