import os


class UnknownDomain(Exception):
    pass


class UnknownLocal(Exception):
    pass


def import_orgmailadmin_models():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orgmailsite.settings')
    import django
    django.setup()
    import orgmailadmin.models
    return orgmailadmin.models


def translate_recipient(recipient):
    try:
        local_part, domain_part = recipient.split('@')
    except ValueError:
        raise ValueError(recipient)
    models = import_orgmailadmin_models()
    try:
        domain = models.Domain.objects.get(name=domain_part)
    except models.Domain.DoesNotExist:
        raise UnknownDomain(recipient)
    try:
        alias = models.Alias.objects.get(
            domain=domain, name=local_part)
    except models.Alias.DoesNotExist:
        raise UnknownLocal(recipient)
    return alias.recipient_list
