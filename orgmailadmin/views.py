import logging
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import TemplateView, FormView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import views as auth_views
from orgmailadmin.models import Domain, Alias, UnknownDomain, UnknownLocal
from orgmailadmin.forms import AliasForm, AuthenticationForm, ImportForm


logger = logging.getLogger('orgmail')


class LoginView(auth_views.LoginView):
    template_name = 'orgmailadmin/login.html'
    form_class = AuthenticationForm


class LogoutView(auth_views.LogoutView):
    template_name = 'orgmailadmin/logged_out.html'


class PasswordChangeView(auth_views.PasswordChangeView):
    template_name = 'orgmailadmin/password_change.html'

    def get_success_url(self):
        return reverse('orgmailadmin:domain_list')


def user_has_domains(user):
    return user.is_authenticated and Domain.objects.filter(users=user).exists()


domains_required = method_decorator(user_passes_test(user_has_domains),
                                    name='dispatch')
superuser_required = method_decorator(
    user_passes_test(lambda u: u.is_superuser), name='dispatch')


@domains_required
class DomainList(TemplateView):
    template_name = 'orgmailadmin/domain_list.html'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        qs = Domain.objects.filter(users=self.request.user)
        qs = qs.annotate(alias_count=Count('alias'))
        qs = qs.order_by('name')
        context_data['object_list'] = qs
        query = self.request.GET.get('q')
        if query:
            try:
                result = Alias.translate_recipient(query)
            except (UnknownDomain, UnknownLocal, ValueError) as exn:
                result = ['%s: %s' % (exn.__class__.__name__, exn)]
            context_data['alias_resolution'] = ', '.join(result)
        return context_data


@domains_required
class DomainUpdate(UpdateView):
    template_name = 'orgmailadmin/domain_update.html'
    model = Domain
    fields = ('description',)

    def get_object(self):
        return get_object_or_404(Domain,
                                 users=self.request.user,
                                 name=self.kwargs['domain_name'])

    def form_valid(self, form):
        logger.info('user:%s domain:%s description=%r',
                    self.request.user.username,
                    self.object.name,
                    form.cleaned_data['description'])
        form.save()
        return redirect('orgmailadmin:domain_list')


@domains_required
class AliasList(TemplateView):
    template_name = 'orgmailadmin/alias_list.html'

    def get_domain(self):
        return get_object_or_404(Domain,
                                 users=self.request.user,
                                 name=self.kwargs['domain_name'])

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        domain = self.get_domain()
        context_data['domain'] = domain
        qs = Alias.objects.filter(domain=domain)
        qs = qs.order_by('name')
        context_data['object_list'] = qs
        return context_data


@domains_required
class AliasCreate(FormView):
    template_name = 'orgmailadmin/alias_form.html'
    form_class = AliasForm

    def get_domain(self):
        return get_object_or_404(Domain,
                                 users=self.request.user,
                                 name=self.kwargs['domain_name'])

    def get_form_kwargs(self, **kwargs):
        form_kwargs = super().get_form_kwargs(**kwargs)
        form_kwargs['domain'] = self.get_domain()
        return form_kwargs

    def form_valid(self, form):
        domain = self.get_domain()
        alias = form.cleaned_data['instance']
        logger.info('user:%s domain:%s %s %s=>%s',
                    self.request.user.username,
                    'update' if alias.pk else 'create',
                    domain.name,
                    alias.name,
                    ','.join(alias.recipient_list))
        form.save()
        domain.save()  # Update domain.modified_time
        return redirect('orgmailadmin:alias_list',
                        domain_name=domain.name)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['domain'] = self.get_domain()
        return context_data


class AliasUpdate(AliasCreate):
    def get_object(self):
        return get_object_or_404(Alias, domain=self.get_domain(),
                                 name=self.kwargs['alias_name'])

    def get_form_kwargs(self, **kwargs):
        form_kwargs = super().get_form_kwargs(**kwargs)
        form_kwargs['instance'] = self.get_object()
        return form_kwargs

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['object'] = self.get_object()
        return context_data


@domains_required
class AliasDelete(DeleteView):
    template_name = 'orgmailadmin/alias_delete.html'

    def get_domain(self):
        return get_object_or_404(Domain,
                                 users=self.request.user,
                                 name=self.kwargs['domain_name'])

    def get_object(self):
        return get_object_or_404(Alias, domain=self.get_domain(),
                                 name=self.kwargs['alias_name'])

    def delete(self, request, *args, **kwargs):
        domain = self.get_domain()
        alias = self.get_object()
        logger.info('user:%s domain:%s delete %s',
                    self.request.user.username,
                    domain.name,
                    alias.name)
        alias.delete()
        domain.save()  # Update domain.modified_time
        return redirect('orgmailadmin:alias_list',
                        domain_name=domain.name)


@superuser_required
class ImportView(FormView):
    template_name = 'orgmailadmin/import_form.html'
    form_class = ImportForm

    def form_valid(self, form):
        saved = form.save([self.request.user])
        if saved:
            logger.info('user:%s imported %s aliases',
                        self.request.user.username,
                        len(saved))
        return redirect('orgmailadmin:domain_list')
