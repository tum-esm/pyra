import pytest

from packages.core import types, utils
from packages.core.utils import exception_email_client
from tests.fixtures import SAMPLE_CONFIG


def test_occurrence_email_renders_exception_fields(monkeypatch: pytest.MonkeyPatch) -> None:
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
