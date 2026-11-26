import pytest
from unittest.mock import MagicMock
from typing import Literal

from packages.core import types, utils
from packages.core.utils import exception_email_client
from tests.fixtures import SAMPLE_CONFIG


@pytest.mark.ci
@pytest.mark.parametrize("port", [465, 587])
def test_smtp_timeout_and_cleanup(monkeypatch: pytest.MonkeyPatch, port: Literal[465, 587]) -> None:
    """Both transports must verify TLS, use a timeout, and close connections on failure."""
    config = SAMPLE_CONFIG.model_copy(deep=True)
    config.general.test_mode = False
    config.error_email.smtp_port = port
    transport = MagicMock()
    connection = transport.return_value
    session = connection.__enter__.return_value
    session.sendmail.side_effect = TimeoutError("SMTP timed out")
    monkeypatch.setattr(
        exception_email_client.smtplib, "SMTP" if port == 587 else "SMTP_SSL", transport
    )
    monkeypatch.setattr(exception_email_client, "_get_pyra_version", lambda: "5.0.0-test")
    monkeypatch.setattr(exception_email_client, "_get_current_log_lines", lambda: [])  # type: ignore

    with pytest.raises(TimeoutError, match="SMTP timed out"):
        utils.ExceptionEmailClient.send_test_email(config)

    assert transport.call_args.kwargs["timeout"] == 30
    context = (
        session.starttls.call_args.kwargs["context"]
        if port == 587
        else transport.call_args.kwargs["context"]
    )
    assert context.check_hostname
    assert context.verify_mode == exception_email_client.ssl.CERT_REQUIRED
    connection.__exit__.assert_called_once()


@pytest.mark.ci
def test_occurrence_email_renders_exception_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep catalog descriptions and occurrence diagnostics in both email formats."""
    sent_email: list[tuple[str, str, str]] = []

    def send_email(config: types.Config, text: str, html: str, subject: str) -> None:
        sent_email.append((text, html, subject))

    monkeypatch.setattr(exception_email_client, "_get_pyra_version", lambda: "5.0.0-test")
    monkeypatch.setattr(exception_email_client, "_get_current_log_lines", lambda: [])  # type: ignore
    monkeypatch.setattr(utils.ExceptionEmailClient, "_send_email", send_email)

    item = types.ExceptionStateItem(
        origin="test",
        exception_type="test-error",
        subject="Test error",
        description="Catalog description",
        traceback="Traceback content",
        details="Occurrence details",
        raised_at=1000.0,
    )
    utils.ExceptionEmailClient.handle_occured_exceptions(
        SAMPLE_CONFIG.model_copy(deep=True), [item]
    )

    assert len(sent_email) == 1
    text, html, subject = sent_email[0]
    for expected in [
        "Catalog description",
        "Occurrence details",
        "Traceback content",
    ]:
        assert expected in text
        assert expected in html
    assert "Test error" in subject
