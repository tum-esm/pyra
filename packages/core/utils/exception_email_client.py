import email.mime.multipart
import email.mime.text
import json
import os
import smtplib
import ssl

from packages.core import types

_dir = os.path.dirname
_PROJECT_DIR = _dir(_dir(_dir(_dir(os.path.abspath(__file__)))))
_PRE_CODE_TAG = '<pre style="background-color: #f1f5f9; color: #334155; padding: 8px 8px 12px 12px; border-radius: 3px; overflow-x: scroll;"><code style="white-space: pre;">'
_POST_CODE_TAG = "</code></pre>"


def _get_pyra_version() -> str:
    """Get the current PYRA version from the UI's package.json file"""

    with open(os.path.join(_PROJECT_DIR, "packages", "ui", "package.json")) as f:
        pyra_version: str = json.load(f)["version"]
    assert pyra_version.startswith("4.")
    return pyra_version


def _get_current_log_lines() -> list[str]:
    """Get the log line from the current info.log file. Only
    returns the log lines from the latest two iterations."""

    try:
        with open(f"{_PROJECT_DIR}/logs/debug.log") as f:
            latest_log_lines = f.readlines()
    except FileNotFoundError:
        return []

    log_lines_in_email: list[str] = []
    included_iterations = 0
    for l in latest_log_lines[::-1][:200]:
        if ("main - INFO - Starting iteration" in l) or ("main - INFO - Starting mainloop" in l):
            included_iterations += 1
        if 'running command "config update" with content:' in l:
            l_sections = l.split('running command "config update" with content:')
            log_lines_in_email.append(
                l_sections[0] + 'running command "config update" with content: { REDACTED }\n'
            )
        else:
            log_lines_in_email.append(l)
        if included_iterations == 2:
            break
    return log_lines_in_email[::-1]


class ExceptionEmailClient:
    """Provide functionality to send emails when an exception
    occurs/is resolved."""

    @staticmethod
    def _send_email(
        config: types.Config,
        text: str,
        html: str,
        subject: str,
    ) -> None:
        smtp_username = config.error_email.smtp_username
        smtp_password = config.error_email.smtp_password

        sender_email = config.error_email.sender_address
        recipients = config.error_email.recipients.replace(" ", "").split(",")

        message = email.mime.multipart.MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"PYRA Technical User <{sender_email}>"
        message["To"] = ", ".join(recipients)

        # The email client will try to render the last part first
        message.attach(email.mime.text.MIMEText(text, "plain"))
        message.attach(email.mime.text.MIMEText(html, "html"))

        if config.general.test_mode:
            return

        # Create secure connection with server and send email
        context = ssl.create_default_context()
        if config.error_email.smtp_port == 587:
            session = smtplib.SMTP(config.error_email.smtp_host, config.error_email.smtp_port)
            session.ehlo()
            session.starttls()
            session.login(config.error_email.smtp_username, config.error_email.smtp_password)
            session.sendmail(sender_email, recipients, message.as_string())
            session.quit()
        else:
            with smtplib.SMTP_SSL(
                config.error_email.smtp_host, config.error_email.smtp_port, context=context
            ) as server:
                server.login(smtp_username, smtp_password)
                server.sendmail(
                    from_addr=sender_email, to_addrs=recipients, msg=message.as_string()
                )

    @staticmethod
    def handle_resolved_exception(config: types.Config) -> None:
        """Send out an email that all exceptions have been resolved."""

        if not config.error_email.notify_recipients:
            return

        pyra_version = _get_pyra_version()
        current_log_lines = _get_current_log_lines()

        logs = "".join(current_log_lines)

        text = (
            "All exceptions have been resolved.\n\n"
            + f"Last 2 iteration's log lines:{logs}\n\n"
            + f"This email has been generated by Pyra {pyra_version} automatically."
        )

        html = "\n".join(
            [
                "<html>",
                '  <body style="color: #0f172a;">',
                '    <p><strong style="color: #16a34a">All exceptions have been resolved.</strong></p>',
                "    <p><strong>Last 2 iteration's log lines:</strong></p>",
                f"    {_PRE_CODE_TAG}{logs}{_POST_CODE_TAG}",
                f"    <p><em>This email has been generated by Pyra {pyra_version} automatically.</em></p>",
                "  </body>",
                "</html>",
            ]
        )

        station_id = config.general.station_id
        subject = f'✅ PYRA on system "{station_id}": all exceptions resolved'
        ExceptionEmailClient._send_email(config, text, html, subject)

    @staticmethod
    def handle_occured_exceptions(
        config: types.Config,
        new_exceptions: list[types.ExceptionStateItem],
    ) -> None:
        """Send out an email that a new exception has occured."""

        if not config.error_email.notify_recipients:
            return

        pyra_version = _get_pyra_version()
        current_log_lines = _get_current_log_lines()
        logs = "".join(current_log_lines)

        text: str = ""
        html: list[str] = []
        for e in new_exceptions:
            text += f"{e.subject} occured inside {e.origin}:\n{e.details}\n\n"
            html += [
                f'   <p><strong><span style="color: #dc2626">{e.subject}</span> occured inside {e.origin}. Details:</strong></p>',
                f"    {_PRE_CODE_TAG}{e.details}{_POST_CODE_TAG}",
            ]

        text_body = (
            f"{text}"
            + f"Last 2 iteration's log lines:{logs}\n"
            + f"This email has been generated by Pyra {pyra_version} automatically."
        )
        html_body = "\n".join(
            [
                "<html>",
                '  <body style="color: #0f172a;">',
                *html,
                "    <p><strong>Last 2 iteration's log lines:</strong></p>",
                f"    {_PRE_CODE_TAG}{logs}{_POST_CODE_TAG}"
                + f"    <p><em>This email has been generated by Pyra {pyra_version} automatically.</em></p>",
                "  </body>",
                "</html>",
            ]
        )

        station_id = config.general.station_id
        subject = f'❗️ PYRA on system "{station_id}": new exceptions ({",".join([e.subject for e in new_exceptions])})'
        ExceptionEmailClient._send_email(config, text_body, html_body, subject)

    @staticmethod
    def send_test_email(config: types.Config) -> None:
        """Send out a test email."""

        pyra_version = _get_pyra_version()
        current_log_lines = _get_current_log_lines()

        logs = "".join(current_log_lines)
        text = (
            "This is a test email.\n\n"
            + f"Last 2 iteration's log lines:{logs}\n\n"
            + f"This email has been generated by Pyra {pyra_version} in a test run."
        )

        html = "\n".join(
            [
                "<html>",
                '  <body style="color: #0f172a;">'
                + '    <p><strong style="color: #16a34a">This is a test email.</strong></p>',
                "    <p><strong>Last 2 iteration's log lines:</strong></p>",
                f"    {_PRE_CODE_TAG}{logs}{_POST_CODE_TAG}",
                f"    <p><em>This email has been generated by Pyra {pyra_version} automatically.</em></p>",
                "  </body>",
                "</html>",
            ]
        )

        station_id = config.general.station_id
        subject = f'⚙️ PYRA on system "{station_id}": test email'
        ExceptionEmailClient._send_email(config, text, html, subject)
