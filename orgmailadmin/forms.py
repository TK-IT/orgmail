import re
import datetime
import contextlib
from django import forms
from django.utils import timezone
from django.contrib.auth import forms as auth_forms
from orgmailadmin.models import Domain, Alias


class AuthenticationForm(auth_forms.AuthenticationForm):
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        qs = Domain.objects.filter(users=user)
        if not qs.exists() and not user.is_superuser:
            raise forms.ValidationError(
                'You have no assigned domains. ' +
                'Contact %s' % settings.MANAGER_NAME)


class AliasForm(forms.Form):
    name = forms.CharField()
    recipients = forms.CharField(widget=forms.Textarea)

    def __init__(self, **kwargs):
        self.domain = kwargs.pop('domain')
        self.instance = kwargs.pop('instance', None)
        super().__init__(**kwargs)
        if self.instance:
            self.initial = dict(name=self.instance.name,
                                recipients=self.instance.recipients)

    def clean(self):
        instance = (
            Alias(domain=self.domain)
            if self.instance is None else self.instance)
        name = self.cleaned_data['name']
        existing = Alias.objects.filter(domain=self.domain)
        if instance.pk:
            existing = existing.exclude(pk=instance.pk)
        existing = existing.filter(name=name)
        if existing.exists():
            self.add_error('name', 'Alias %r already exists.' % name)
            return
        instance.name = name
        instance.recipients = self.cleaned_data['recipients']
        instance.clean()
        return {'instance': instance}

    def save(self):
        instance = self.cleaned_data['instance']
        instance.save()
        return instance


def parse_datetime(s):
    format = '%Y-%m-%d %H:%M:%S'
    return timezone.make_aware(datetime.datetime.strptime(s, format))


@contextlib.contextmanager
def suppress_datetime_auto(field):
    a = field.auto_now
    b = field.auto_now_add
    field.auto_now = field.auto_now_add = False
    try:
        yield
    finally:
        field.auto_now = a
        field.auto_now_add = b


class ImportForm(forms.Form):
    data = forms.CharField(widget=forms.Textarea)

    def clean(self):
        string = self.cleaned_data['data']
        if 'INSERT INTO alias' not in string:
            raise forms.ValidationError(
                'You must input a backup from Postfixadmin ' +
                'containing "INSERT INTO alias" statements.')
        pattern = (
            r"INSERT INTO alias " +
            r"\(address,goto,domain,created,modified,active\) VALUES " +
            r"\('([^']+)','([^']+)','([^']+)','([^']+)','([^']+)','([^']+)'\)")
        matches = re.finditer(pattern, string)
        models = []
        for mo in matches:
            address, goto, domain, created, modified, active = mo.groups()
            recipients = goto.replace(',', '\n')
            try:
                address_local, address_domain = address.split('@')
            except ValueError:
                raise forms.ValidationError('invalid address %r' % address)
            if address_domain != domain:
                raise forms.ValidationError('domain mismatch in %r and %r' %
                                            (address, domain))
            name = address_local if address_local != '' else '*'
            o = Alias(name=name, recipients=recipients,
                      created_time=created, modified_time=modified)
            o.domain_name = domain
            models.append(o)
        if not models:
            raise forms.ValidationError('No INSERT INTO statements matched')
        self.cleaned_data['models'] = models

    def save(self, new_domain_users):
        domains = {domain.name: domain for domain in Domain.objects.all()}
        qs = Alias.objects.all().select_related()
        existing = {(alias.domain.name, alias.name): alias for alias in qs}
        aliases = self.cleaned_data['models']
        created = Alias._meta.get_field('created_time')
        modified = Alias._meta.get_field('modified_time')
        saved = []
        with suppress_datetime_auto(created), suppress_datetime_auto(modified):
            for a in aliases:
                if (a.domain_name, a.name) in existing:
                    continue
                try:
                    a.domain = domains[a.domain_name]
                except KeyError:
                    d = domains[a.domain_name] = Domain(name=a.domain_name)
                    d.clean()
                    d.save()
                    # Now that d has a pk, we can set d.users and a.domain_id
                    d.users = new_domain_users
                    a.domain = d
                a.clean()
                a.save()
                saved.append(a)
                existing[a.domain.name, a.name] = a
        return saved
