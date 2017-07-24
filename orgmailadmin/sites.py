class OrgmailadminSite(object):
    name = 'orgmailadmin'

    def get_urls(self):
        from django.conf.urls import url
        from orgmailadmin import views

        urls = [
            url(r'^login/$', views.LoginView.as_view(), name='login'),
            url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
            url(r'^password_change/$', views.PasswordChangeView.as_view(),
                name='password_change'),
            url(r'^$', views.DomainList.as_view(), name='domain_list'),
            url(r'^import/$', views.ImportView.as_view(), name='import'),
            url(r'^(?P<domain_name>[^/]+)/details/$',
                views.DomainUpdate.as_view(), name='domain_update'),
            url(r'^(?P<domain_name>[^/]+)/$',
                views.AliasList.as_view(), name='alias_list'),
            url(r'^(?P<domain_name>[^/]+)/new/$',
                views.AliasCreate.as_view(), name='alias_create'),
            url(r'^(?P<domain_name>[^/]+)/alias/(?P<alias_name>[^/]+)/$',
                views.AliasUpdate.as_view(), name='alias_update'),
            url(r'^(?P<domain_name>[^/]+)/alias/(?P<alias_name>[^/]+)/delete/$',
                views.AliasDelete.as_view(), name='alias_delete'),
        ]
        return urls

    @property
    def urls(self):
        return self.get_urls(), 'orgmailadmin', self.name


site = OrgmailadminSite()
