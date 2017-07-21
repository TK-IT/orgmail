from django import forms
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
        return {'instance': instance}

    def save(self):
        instance = self.cleaned_data['instance']
        instance.save()
        return instance
