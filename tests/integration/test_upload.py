import subprocess
import json
import invoke
import paramiko
import os
import time
import fabric.connection, fabric.transfer
from ..fixtures import original_config, populated_upload_test_directories

dir = os.path.dirname
PROJECT_DIR = dir(dir(dir(os.path.abspath(__file__))))

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
            f"python3.10 {dir_path}/get_upload_dir_checksum.py {dir_path}/{date}", hide=True
        )
        assert p.exited == 0
        checksums.append(date + ":" + p.stdout.strip())

    return ",".join(checksums)


def test_upload(original_config, populated_upload_test_directories) -> None:
    upload_config = original_config["upload"]
    assert upload_config is not None, "config.upload is null"

    ifg_dates = populated_upload_test_directories["ifg_dates"]
    helios_dates = populated_upload_test_directories["helios_dates"]

    try:
        connection = fabric.connection.Connection(
            f"{upload_config['user']}@{upload_config['host']}",
            connect_kwargs={"password": upload_config["password"]},
            connect_timeout=5,
        )
        transfer_process = fabric.transfer.Transfer(connection)
    except TimeoutError as e:
        raise Exception("could not reach host")
    except paramiko.ssh_exception.AuthenticationException as e:
        raise Exception("failed to authenticate")

    src_dir_ifgs = os.path.join(PROJECT_DIR, "test-tmp")
    src_dir_helios = os.path.join(PROJECT_DIR, "logs", "helios")

    # set up test directories
    dst_test_dir = f"/tmp/pyra-upload-test-{int(time.time())}"
    dst_test_dir_ifgs = f"{dst_test_dir}/ifgs"
    dst_test_dir_helios = f"{dst_test_dir}/helios"
    assert transfer_process.is_remote_dir("/tmp")
    assert not transfer_process.is_remote_dir(dst_test_dir)
    connection.run(f"mkdir {dst_test_dir}")
    connection.run(f"mkdir {dst_test_dir_ifgs}")
    connection.run(f"mkdir {dst_test_dir_helios}")
    assert transfer_process.is_remote_dir(dst_test_dir_ifgs)
    assert transfer_process.is_remote_dir(dst_test_dir_helios)

    upload_config = {
        **upload_config,
        "upload_ifgs": True,
        "src_directory_ifgs": src_dir_ifgs,
        "dst_directory_ifgs": dst_test_dir_ifgs,
        "remove_src_ifgs_after_upload": False,
        "upload_helios": True,
        "dst_directory_helios": dst_test_dir_helios,
        "remove_src_helios_after_upload": False,
    }
    with open(os.path.join(PROJECT_DIR, "config", "config.json"), "w") as f:
        json.dump({**original_config, "upload": upload_config}, f)

    checksums = {
        "initial": {
            "ifgs": get_local_checksum(src_dir_ifgs, ifg_dates),
            "helios": get_local_checksum(src_dir_helios, helios_dates),
        }
    }
    print(checksums)
    assert False

    # TODO: trigger headless upload process

    # TODO: Assert existence of checksum script on remote
    # TODO: calculate checksum on remote
    # TODO: calculate checksum locally (a second time)

    # TODO: Assert equality of all three checksums

    # TODO: Upload again, now with "remove" flag set
    # TODO: Assert that local directories are empty
    # TODO: Calculate remote checksum
    # TODO: Assert equality to first three checksums
