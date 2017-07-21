from emailtunnel import (
    SMTPForwarder, Message, InvalidRecipient, Envelope, logger,
)
from emailtunnel.mailhole import MailholeRelayMixin

from orgmail import (
    translate_recipient, UnknownDomain, UnknownLocal,
)


class OrgmailForwarder(SMTPForwarder, MailholeRelayMixin):
    MAIL_FROM = 'admin@TAAGEKAMMERET.dk'

    def get_mailhole_key(self):
        return os.getenv('MAILHOLE_KEY')

    def should_mailhole(self, message, recipient, sender):
        # Send everything to mailhole
        return True

    def translate_recipient(self, rcptto):
        try:
            return translate_recipient(rcptto)
        except (UnknownDomain, UnknownLocal) as exn:
            raise InvalidRecipient(
                '%s: %s' % (exn.__class__.__name__, exn))

    def get_envelope_mailfrom(self, envelope, recipients=None):
        return self.__class__.MAIL_FROM
