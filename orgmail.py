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
    models = import_orgmailadmin_models()

    domains = {domain.name: domain
               for domain in models.Domain.objects.all()}

    resolved = {}

    def resolve(recipient):
        try:
            return resolved[recipient]
        except KeyError:
            pass
        try:
            local_part, domain_name = recipient.split('@')
        except ValueError:
            raise ValueError(recipient)
        try:
            domain = domains[domain_name]
        except KeyError:
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

        resolved[recipient] = ()
        result = []
        for r in alias.recipient_list:
            try:
                result.extend(resolve(r))
            except UnknownDomain:
                result.append(r)
            except UnknownLocal:
                pass
        resolved[recipient] = result
        return result

    try:
        return resolve(recipient)
    finally:
        from django.db import connection
        connection.close()
