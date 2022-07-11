from packages.core.utils import ConfigInterface, ExceptionEmailClient


def test_emailing():
    _CONFIG = ConfigInterface().read()

    try:
        raise Exception("some exception name")
    except Exception as e:
        ExceptionEmailClient.handle_occured_exception(_CONFIG, e)
        ExceptionEmailClient.handle_resolved_exception(_CONFIG)
