from django import forms
from orgmailadmin.models import Alias


class AliasForm(forms.Form):
    name = forms.CharField()
    recipients = forms.CharField(widget=forms.Textarea)

    def __init__(self, **kwargs):
        self.domain = kwargs.pop('domain')
        self.instance = kwargs.pop('instance', None)
        super().__init__(**kwargs)

    def clean(self):
        instance = (
            Alias(domain=self.domain)
            if self.instance is None else self.instance)
        instance.name = self.cleaned_data['name']
        instance.recipients = self.cleaned_data['recipients']
        return {'instance': instance}

    def save(self):
        instance = self.cleaned_data['instance']
        instance.save()
        return instance
