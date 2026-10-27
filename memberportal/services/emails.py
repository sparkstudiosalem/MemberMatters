from django.template.loader import render_to_string
from django.utils.html import escape
from constance import config
from postmarker.core import PostmarkClient, ClientError
import logging
import json
import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger("emails")


def send_single_email(
    to_email: object,
    subject: object,
    template_vars: object,
    template_name=None,
    reply_to=None,
    user: object | None = None,
) -> object:
    template_to_use = template_name if template_name else "email_without_button.html"
    logger.debug("Using email template: " + template_to_use)
    logger.debug("Using template vars: " + json.dumps(template_vars))

    if template_vars.get("message"):
        template_vars["message"] = escape(template_vars["message"]).replace(
            "~br~", "<br>"
        )

    email_string = render_to_string(
        template_to_use, {"email": template_vars, "config": config}
    )

    from_email = getattr(config, "EMAIL_DEFAULT_FROM", None) or os.environ.get("EMAIL_DEFAULT_FROM") or os.environ.get("EMAIL_HOST_USER") or "info@sparkstudiosalem.com"

    # If POSTMARK_API_KEY is configured (and not the default placeholder), send via Postmark
    if config.POSTMARK_API_KEY and config.POSTMARK_API_KEY not in ("PLEASE_CHANGE_ME", ""):
        postmark = PostmarkClient(server_token=config.POSTMARK_API_KEY)
        try:
            postmark.emails.send(
                From=from_email,
                To=to_email,
                Subject=subject,
                HtmlBody=email_string,
                ReplyTo=reply_to or from_email,
            )
        except ClientError as e:
            code = e.error_code
            if code == 406:
                if user:
                    logger.warning("Email NOT sent because recipient is INACTIVE in postmark")
                    user.log_event(
                        "Email NOT sent because recipient is INACTIVE in postmark: ",
                        "email",
                        "Email content: " + json.dumps(template_vars),
                    )
            else:
                logger.error("Error sending email via Postmark: " + str(e))
                raise e

        if user:
            logger.info("Email sent to " + str(to_email) + " with subject: " + str(subject))
            user.log_event(
                "Sent email with subject: " + str(subject),
                "email",
                "Email content: " + json.dumps(template_vars),
            )
    else:
        # Standard SMTP (Gmail / Google Workspace compatible Python 3.12 smtplib)
        try:
            email_host = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
            email_port = int(os.environ.get("EMAIL_PORT", "587"))
            email_user = os.environ.get("EMAIL_HOST_USER", "notifications@sparkstudiosalem.com")
            email_password = os.environ.get("EMAIL_HOST_PASSWORD", "")
            use_tls = os.environ.get("EMAIL_USE_TLS", "True").lower() in ("true", "1", "yes")

            target_recipients = [to_email] if isinstance(to_email, str) else list(to_email)

            context = ssl.create_default_context()
            with smtplib.SMTP(email_host, email_port, timeout=30) as server:
                if use_tls:
                    server.starttls(context=context)
                if email_user and email_password:
                    server.login(email_user, email_password)

                msg = MIMEMultipart("alternative")
                msg["Subject"] = str(subject)
                msg["From"] = from_email
                msg["To"] = ", ".join(target_recipients)
                msg["Reply-To"] = reply_to or from_email

                plain_body = template_vars.get("message", "") or str(subject)
                msg.attach(MIMEText(plain_body, "plain", "utf-8"))
                msg.attach(MIMEText(email_string, "html", "utf-8"))

                server.sendmail(from_email, target_recipients, msg.as_string())

            logger.info("SMTP email sent to " + str(to_email) + " with subject: " + str(subject))
            if user:
                user.log_event(
                    "Sent SMTP email with subject: " + str(subject),
                    "email",
                    "Email content: " + json.dumps(template_vars),
                )
        except Exception as e:
            logger.error("Error sending SMTP email: " + str(e))
            if user:
                user.log_event(
                    "Failed to send SMTP email with subject: " + str(subject) + ": " + str(e),
                    "email",
                    "Email content: " + json.dumps(template_vars),
                )
            raise e

    return True


def send_email_to_admin(
    subject: object,
    template_vars: object,
    template_name=None,
    reply_to=None,
    user: object | None = None,
) -> object:
    admin_email = getattr(config, "EMAIL_ADMIN", None) or os.environ.get("EMAIL_ADMIN") or "info@sparkstudiosalem.com"
    return send_single_email(
        admin_email,
        subject,
        template_vars,
        template_name=template_name,
        reply_to=reply_to,
        user=user,
    )
