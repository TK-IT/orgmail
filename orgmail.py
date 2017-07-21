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

    try:
        return models.Alias.translate_recipient(recipient)
    finally:
        from django.db import connection
        connection.close()
