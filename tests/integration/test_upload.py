import subprocess
import json
import sys
import invoke
import paramiko
import os
import time
import pytest
import fabric.connection, fabric.transfer
from ..fixtures import original_config, populated_upload_test_directories, fabric_connection

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(os.path.abspath(__file__))))
sys.path.append(PROJECT_DIR)

from packages.core import threads

# TODO: in headless-upload mode, do not loop infinitely
# TODO: test without removal (+ rerunning)
# TODO: test with removal

# 1. Before upload, create a dst dir that does not
#    exist on the remote dir
# 2. After upload, download dst dir and compare to
#    original dir using the "diff" command


def get_local_checksum(dir_path: str, dates: list[str]) -> str:
    checksums = []
    for date in sorted(dates):
        p = subprocess.run(
            [
                "python",
                os.path.join(PROJECT_DIR, "scripts", "get_upload_dir_checksum.py"),
                os.path.join(dir_path, date),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        assert p.returncode == 0
        checksums.append(date + ":" + p.stdout.decode().strip())

    return ",".join(checksums)


def get_remote_checksum(
    dir_path: str, dates: list[str], connection: fabric.connection.Connection
) -> str:
    checksums = []

    for date in sorted(dates):
        p: invoke.runners.Result = connection.run(
            f"python3.10 {dir_path}/get_upload_dir_checksum.py {dir_path}/{date}",
            hide=True,
            in_stream=False,
        )
        assert p.exited == 0
        checksums.append(date + ":" + p.stdout.strip())

    return ",".join(checksums)


def assert_remote_meta_completeness(
    dir_path: str, dates: list[str], connection: fabric.connection.Connection
) -> str:
    for date in sorted(dates):
        p: invoke.runners.Result = connection.run(
            f"cat {dir_path}/{date}/upload-meta.json", hide=True, in_stream=False
        )
        assert p.exited == 0
        assert '"complete": true' in p.stdout.strip()


@pytest.mark.integration
def test_upload(original_config, populated_upload_test_directories, fabric_connection) -> None:
    upload_config = original_config["upload"]
    assert upload_config is not None, "config.upload is null"

    ifg_dates = populated_upload_test_directories["ifg_dates"]
    helios_dates = populated_upload_test_directories["helios_dates"]

    try:
        connection: fabric.connection.Connection = fabric_connection
        transfer_process = fabric.transfer.Transfer(connection)
        connection.open()
        assert connection.is_connected
    except TimeoutError:
        raise Exception("could not reach host")
    except paramiko.ssh_exception.AuthenticationException:
        raise Exception("failed to authenticate")

    src_dir_ifgs = os.path.join(PROJECT_DIR, "test-tmp")
    src_dir_helios = os.path.join(PROJECT_DIR, "logs", "helios")

    # set up test directories
    dst_dir = f"/tmp/pyra-upload-test-{int(time.time())}"
    dst_dir_ifgs = f"{dst_dir}/ifgs"
    dst_dir_helios = f"{dst_dir}/helios"
    assert transfer_process.is_remote_dir("/tmp")
    assert not transfer_process.is_remote_dir(dst_dir)
    connection.run(f"mkdir {dst_dir}", hide=True, in_stream=False)
    connection.run(f"mkdir {dst_dir_ifgs}", hide=True, in_stream=False)
    connection.run(f"mkdir {dst_dir_helios}", hide=True, in_stream=False)
    assert transfer_process.is_remote_dir(dst_dir_ifgs)
    assert transfer_process.is_remote_dir(dst_dir_helios)

    upload_config = {
        **upload_config,
        "upload_ifgs": True,
        "src_directory_ifgs": src_dir_ifgs,
        "dst_directory_ifgs": dst_dir_ifgs,
        "remove_src_ifgs_after_upload": False,
        "upload_helios": True,
        "dst_directory_helios": dst_dir_helios,
        "remove_src_helios_after_upload": False,
    }
    config = json.loads(json.dumps(original_config))
    config["general"]["test_mode"] = False
    config["upload"] = upload_config
    with open(os.path.join(PROJECT_DIR, "config", "config.json"), "w") as f:
        json.dump(config, f)

    checksums = {
        "local-1": {
            "ifgs": get_local_checksum(src_dir_ifgs, ifg_dates),
            "helios": get_local_checksum(src_dir_helios, helios_dates),
        }
    }
    threads.UploadThread(config).main(headless=True)

    checksums["remote-1"] = {
        "ifgs": get_remote_checksum(dst_dir_ifgs, ifg_dates, connection),
        "helios": get_remote_checksum(dst_dir_helios, helios_dates, connection),
    }
    checksums["local-2"] = {
        "ifgs": get_local_checksum(src_dir_ifgs, ifg_dates),
        "helios": get_local_checksum(src_dir_helios, helios_dates),
    }
    print(json.dumps(checksums, indent=4))

    # check whether the dst is equal to the initial source
    assert checksums["local-1"]["ifgs"] == checksums["remote-1"]["ifgs"]
    assert checksums["local-1"]["helios"] == checksums["remote-1"]["helios"]

    # check whether the src has not been changed
    assert checksums["local-1"]["ifgs"] == checksums["local-2"]["ifgs"]
    assert checksums["local-1"]["helios"] == checksums["local-2"]["helios"]

    # check if every remote meta contains "complete=true"
    assert_remote_meta_completeness(dst_dir_ifgs, ifg_dates, connection)
    assert_remote_meta_completeness(dst_dir_helios, helios_dates, connection)

    # upload again, now with "remove" flag set
    config["upload"]["remove_src_ifgs_after_upload"] = True
    config["upload"]["remove_src_helios_after_upload"] = True
    with open(os.path.join(PROJECT_DIR, "config", "config.json"), "w") as f:
        json.dump(config, f)

    threads.UploadThread(config).main(headless=True)

    # check whether the local directories are empty
    for date in ifg_dates:
        assert not os.path.isdir(os.path.join(src_dir_ifgs, date))
    for date in helios_dates:
        assert not os.path.isdir(os.path.join(src_dir_helios, date))

    # check whether the dst has not been changed
    checksums["remote-2"] = {
        "ifgs": get_remote_checksum(dst_dir_ifgs, ifg_dates, connection),
        "helios": get_remote_checksum(dst_dir_helios, helios_dates, connection),
    }
    print(json.dumps(checksums, indent=4))
    assert checksums["local-1"]["ifgs"] == checksums["remote-2"]["ifgs"]
    assert checksums["local-1"]["helios"] == checksums["remote-2"]["helios"]

    # check if every remote meta contains "complete=true"
    assert_remote_meta_completeness(dst_dir_ifgs, ifg_dates, connection)
    assert_remote_meta_completeness(dst_dir_helios, helios_dates, connection)