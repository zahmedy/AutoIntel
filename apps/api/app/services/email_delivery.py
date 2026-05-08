import logging

import boto3

from app.core.config import settings

logger = logging.getLogger("uvicorn.error")


def send_email_code(email: str, code: str) -> None:
    subject = "Your NicheRides verification code"
    body = (
        f"Your NicheRides verification code is {code}.\n\n"
        f"This code expires in {settings.EMAIL_CODE_TTL_MINUTES} minutes."
    )

    if not settings.EMAIL_FROM:
        logger.info("Email verification code for %s: %s", email, code)
        return

    client_kwargs = {
        "region_name": settings.AWS_SES_REGION,
    }
    if settings.AWS_SES_ACCESS_KEY_ID and settings.AWS_SES_SECRET_ACCESS_KEY:
        client_kwargs["aws_access_key_id"] = settings.AWS_SES_ACCESS_KEY_ID
        client_kwargs["aws_secret_access_key"] = settings.AWS_SES_SECRET_ACCESS_KEY
    if settings.AWS_SES_SESSION_TOKEN:
        client_kwargs["aws_session_token"] = settings.AWS_SES_SESSION_TOKEN

    client = boto3.client("ses", **client_kwargs)
    client.send_email(
        Source=settings.EMAIL_FROM,
        Destination={"ToAddresses": [email]},
        Message={
            "Subject": {"Data": subject, "Charset": "UTF-8"},
            "Body": {"Text": {"Data": body, "Charset": "UTF-8"}},
        },
    )
