# Third-party
from flask_security.forms import RegisterFormV2
from wtforms import ValidationError

# Local
from .email_verification import verify_email


class VerifiedRegisterForm(RegisterFormV2):
    def validate_email(self, field):
        verdict = verify_email(field.data)
        if verdict is False:
            raise ValidationError(
                "This email address could not be verified. Please check it and try again."
            )