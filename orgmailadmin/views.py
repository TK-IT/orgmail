from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView, FormView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import views as auth_views
from orgmailadmin.models import Domain, Alias
from orgmailadmin.forms import AliasForm, AuthenticationForm, ImportForm


class LoginView(auth_views.LoginView):
    template_name = 'orgmailadmin/login.html'
    form_class = AuthenticationForm


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
            context_data['alias_resolution'] = ', '.join(
                Alias.translate_recipient(query))
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

    def get_success_url(self):
        return reverse('orgmailadmin:domain_list')


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
        form.save()
        domain = self.get_domain()
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

    def form_valid(self, form):
        form.save()
        domain = self.get_domain()
        domain.save()  # Update domain.modified_time
        return redirect('orgmailadmin:alias_list',
                        domain_name=domain.name)


@superuser_required
class ImportView(FormView):
    template_name = 'orgmailadmin/import_form.html'
    form_class = ImportForm

    def form_valid(self, form):
        form.save([self.request.user])
        return redirect('orgmailadmin:domain_list')
