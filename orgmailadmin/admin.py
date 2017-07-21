from django.contrib import admin


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Alias)
class AliasAdmin(admin.ModelAdmin):
    list_display = ('name', 'domain')
