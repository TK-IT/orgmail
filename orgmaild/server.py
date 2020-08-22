import email.utils
from emailtunnel import (
    SMTPForwarder, Message, InvalidRecipient, Envelope, logger,
)
from emailtunnel.mailhole import MailholeRelayMixin

from orgmail import (
    translate_recipient, UnknownDomain, UnknownLocal,
)


class OrgmailForwarder(SMTPForwarder, MailholeRelayMixin):
    MAIL_FROM = 'admin@TAAGEKAMMERET.dk'

    REWRITE_FROM = True
    STRIP_HTML = True

    def __init__(self, receiver_host, receiver_port):
        # Set relay_host to 0.0.0.0 to ensure that no mail is relayed via SMTP.
        super().__init__(receiver_host, receiver_port, '0.0.0.0', 25)

    def startup_log(self):
        logger.info('orgmaild listening on %s:%s' % (self.host, self.port))

    def should_mailhole(self, message, recipient, sender):
        # Send everything to mailhole
        return True

    def translate_recipient(self, rcptto):
        try:
            return translate_recipient(rcptto, count_hit=True)
        except (UnknownDomain, UnknownLocal) as exn:
            raise InvalidRecipient(
                '%s: %s' % (exn.__class__.__name__, exn))

    def get_envelope_mailfrom(self, envelope, recipients=None):
        return self.__class__.MAIL_FROM

    def forward(self, original_envelope, message, recipients, sender):
        if self.REWRITE_FROM:
            del message.message["DKIM-Signature"]
            original_domain = original_envelope.rcpttos[0].split("@")[1]
            orig_from = message.get_header("From")
            parsed = email.utils.getaddresses([orig_from])
            orig_name = parsed[0][0]
            name = "%s via %s" % (orig_name, original_domain)
            addr = "postmaster@%s" % original_domain
            new_from = email.utils.formataddr((name, addr))
            message.set_unique_header("From", new_from)
            message.set_unique_header("Reply-To", orig_from)
        if self.STRIP_HTML:
            from emailtunnel.extract_text import get_body_text

            del message.message["DKIM-Signature"]
            t = get_body_text(message.message)
            message.set_unique_header("Content-Type", "text/plain")
            del message.message["Content-Transfer-Encoding"]
            charset = email.charset.Charset("utf-8")
            charset.header_encoding = charset.body_encoding = email.charset.QP
            message.message.set_payload(t, charset=charset)

        super().forward(original_envelope, message, recipients, sender)
