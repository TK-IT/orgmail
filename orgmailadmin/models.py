from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from orgmail import UnknownDomain, UnknownLocal


class Domain(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=100, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    users = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.name


class Alias(models.Model):
    CATCHALL_NAME = '*'

    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    recipients = models.TextField()

    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [
            ('domain', 'name'),
        ]

    def clean(self):
        from_address = '%s@%s' % (self.name, self.domain.name)
        for r in self.recipient_list:
            if r == from_address:
                raise ValidationError('Circular alias %s -> %s' % (self, r))
            if r.count('@') != 1:
                raise ValidationError('Each address must have one "@": %r' % r)
            if r.strip('@').count('@') != 1:
                raise ValidationError('Empty localpart/domain: %r' % r)

    @property
    def recipient_list(self):
        return [r.strip() for r in self.recipients.splitlines() if r.strip()]

    def __str__(self):
        return '%s@%s' % (self.name, self.domain.name)

    @staticmethod
    def translate_recipient(recipient):
        domains = {domain.name: domain
                   for domain in Domain.objects.all()}

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
                alias = Alias.objects.get(
                    domain=domain, name=local_part)
            except Alias.DoesNotExist:
                try:
                    # Catch-all
                    alias = Alias.objects.get(
                        domain=domain, name=Alias.CATCHALL_NAME)
                except Alias.DoesNotExist:
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

        return sorted(set(resolve(recipient)))
