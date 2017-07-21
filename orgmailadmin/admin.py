from django.contrib import admin
from orgmailadmin.models import Domain, Alias


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Alias)
class AliasAdmin(admin.ModelAdmin):
    list_display = ('name', 'domain')
