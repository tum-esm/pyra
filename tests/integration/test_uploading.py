import circadian_scp_upload
import pytest
from packages.core import types


@pytest.mark.order(2)
@pytest.mark.integration
def test_uploading() -> None:
    config = types.Config.load()
    if config.upload is None:
        return

    with circadian_scp_upload.RemoteConnection(
        config.upload.host.root,
        config.upload.user,
        config.upload.password,
    ) as remote_connection:
        if remote_connection.connection.is_connected:
            return

    raise Exception("`circadian_scp_upload` should have raised an error")
