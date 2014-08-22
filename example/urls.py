from django.conf.urls import patterns, include, url

from django.contrib import admin
from example.our_calendar.views import OurCalendarView

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'test_project.views.home', name='home'),
    # url(r'^test_project/', include('test_project.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^calendar(?P<path>.*)$', OurCalendarView.as_view()),
    url(r'^calendar(?P<path>.*)/$', OurCalendarView.as_view()),
)
