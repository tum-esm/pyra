from packages.core import utils, interfaces


def test_emailing() -> None:
    _CONFIG = interfaces.ConfigInterface().read()

    try:
        raise Exception("some exception name")
    except Exception as e:
        utils.ExceptionEmailClient.handle_occured_exception(_CONFIG, e)
        utils.ExceptionEmailClient.handle_resolved_exception(_CONFIG)
