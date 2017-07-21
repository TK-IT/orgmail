import os


class UnknownDomain(Exception):
    pass


class UnknownLocal(Exception):
    pass


def import_orgmailadmin_models():
    import json

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(BASE_DIR, 'env.json')) as fp:
        os.environ.update(json.load(fp))

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
        try:
            domain = models.Domain.objects.get(name=domain_part)
        except models.Domain.DoesNotExist:
            raise UnknownDomain(recipient)
        try:
            alias = models.Alias.objects.get(
                domain=domain, name=local_part)
        except models.Alias.DoesNotExist:
            try:
                # Catch-all
                alias = models.Alias.objects.get(
                    domain=domain, name=models.Alias.CATCHALL_NAME)
            except models.Alias.DoesNotExist:
                raise UnknownLocal(recipient)
        return alias.recipient_list
    finally:
        from django.db import connection
        connection.close()
