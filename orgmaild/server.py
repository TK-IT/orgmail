from emailtunnel import (
    SMTPForwarder, Message, InvalidRecipient, Envelope, logger,
)
from emailtunnel.mailhole import MailholeRelayMixin

from orgmail import (
    translate_recipient, UnknownDomain, UnknownLocal,
)


class OrgmailForwarder(SMTPForwarder, MailholeRelayMixin):
    MAIL_FROM = 'admin@TAAGEKAMMERET.dk'

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
