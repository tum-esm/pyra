import contextlib
from typing import Iterator
from packages.core import types

import fabric.connection, fabric.transfer


class SSHInterface:
    @staticmethod
    class ConnectionError(Exception):
        """raised when SSH connection could not be established"""

    @staticmethod
    @contextlib.contextmanager
    def use(
        config: types.ConfigDict,
    ) -> Iterator[tuple[fabric.connection.Connection, fabric.transfer.Transfer]]:
        assert config["upload"] is not None

        try:
            connection = fabric.connection.Connection(
                f"{config['upload']['user']}@{config['upload']['host']}",
                connect_kwargs={"password": config["upload"]["password"]},
                connect_timeout=5,
            )
            transfer_process = fabric.transfer.Transfer(connection)

            connection.open()
            assert connection.is_connected, "could not open the connection"

            yield (connection, transfer_process)
        except Exception as e:
            raise SSHInterface.ConnectionError(e)
        finally:
            connection.close()
