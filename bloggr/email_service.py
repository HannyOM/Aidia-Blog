import resend
from flask_security.mail_util import MailUtil
from typing import List


class ResendEmailService:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        resend.api_key = app.config.get("RESEND_API_KEY")
        self.from_email = app.config.get("RESEND_FROM_EMAIL")

    def send_email(
        self,
        to: List[str],
        subject: str,
        html: str,
        text: str | None = None,
        from_email: str | None = None,
        reply_to: List[str] | None = None,
    ):
        params: resend.Emails.SendParams = {
            "from": from_email or self.from_email,
            "to": to,
            "subject": subject,
            "html": html,
        }
        if text:
            params["text"] = text
        if reply_to:
            params["reply_to"] = reply_to

        return resend.Emails.send(params)


class ResendMailUtil(MailUtil):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self._email_service = ResendEmailService()
        self._email_service.init_app(app)

    def send_mail(self, template, subject, recipient, sender, body, html, **kwargs):
        formatted_sender = self._format_sender(sender)
        self._email_service.send_email(
            to=[recipient] if isinstance(recipient, str) else recipient,
            subject=str(subject),
            html=html or body,
            text=body,
            from_email=formatted_sender,
        )

    def _format_sender(self, sender):
        if sender is None:
            return self._email_service.from_email
        if isinstance(sender, tuple):
            name, email = sender
            return f"{name} <{email}>" if name else email
        return sender

    def send_message(self, msg):
        to = list(msg.send_to) if hasattr(msg, "send_to") else []
        if not to:
            return
        formatted_sender = self._format_sender(msg.sender)
        self._email_service.send_email(
            to=to,
            subject=str(msg.subject),
            html=msg.body,
            from_email=formatted_sender,
        )


email_service = ResendEmailService()
