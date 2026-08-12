# Standard library
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

# Third-party
from flask import current_app

DEFAULT_API_URL = "https://apilayer.net/api/check"
TIMEOUT_SECONDS = 10


def verify_email(email: str) -> bool | None:
    """Check whether an email address is deliverable.

    Uses the Mailboxlayer API. Returns ``False`` when the address is
    hard-invalid, ``True`` when it is deliverable or only risky, and
    ``None`` when verification is skipped (no access key) or the API
    check fails. The app treats ``None`` as "allow registration".

    Only the fields that are reliable on the free tier are used to block.
    The SMTP check (``smtp_check``) is disabled/throttled on the free plan
    and commonly returns ``false`` for legitimate mail servers, so it is
    not used as a blocking signal.
    """
    access_key = current_app.config.get("MAILBOXLAYER_ACCESS_KEY")
    if not access_key:
        return None
    if not email:
        return None

    api_url = current_app.config.get("MAILBOXLAYER_API_URL") or DEFAULT_API_URL
    query = urlencode({"access_key": access_key, "email": email})

    try:
        request = Request(f"{api_url}?{query}", method="GET")
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        current_app.logger.warning("Mailboxlayer verification failed for %s: %s", email, exc)
        return None

    if not data.get("success", True):
        info = data.get("error", {}).get("info", "unknown error")
        current_app.logger.warning("Mailboxlayer error for %s: %s", email, info)
        return None

    if data.get("format_valid") is False:
        return False
    if data.get("mx_found") is False:
        return False
    return True