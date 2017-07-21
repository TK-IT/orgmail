from django.db import models
from django.contrib.auth.models import User


class Domain(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=100, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)
    users = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.name


class Alias(models.Model):
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)
    recipients = models.TextField()

    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    @property
    def recipient_list(self):
        return [r.strip() for r in self.recipients.splitlines() if r.strip()]

    def __str__(self):
        return '%s@%s' % (self.name, self.domain.name)
