from django.conf.urls import include, url
#from django.views.generic.edit import CreateView
#from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import views as auth_views

from . import views

app_name = 'recommender'
urlpatterns = [
    url(r'^$', views.index, name='index'), # can also pass kwargs={...}
    url(r'^profile/$', views.profile, name='profile'),
#    url(r'^history/(?P<page_number>[0-9]+)$', views.history, name='history'),
    url(r'^history/$', views.history, name='history'),
    url(r'^eat/(?P<food_ID>[0-9]+)$', views.eat_ID, name='eat_ID'),
    url('^', include('django.contrib.auth.urls')),
    url(r'^accounts/login/$', auth_views.login, {'redirect_field_name': 'recommender/index.html'}),
    url(r'^accounts/logout/$', auth_views.logout_then_login), #{'login_url': '/accounts/login'}),
    url(r'^register/$', views.register, name='register'),
    url(r'^register/complete/$', views.registration_complete, name='registration_complete'),
    url(r'^reset/$', views.reset, name='reset'),
    url(r'^plot_history.png$', views.plot_history, name='plot_history')
#    url(r'^login/$', 'django.contrib.auth.views.login', {
#    'template_name': 'recommender/login.html'
#    }),
#    url('^register/', CreateView.as_view(
#            template_name='recommender/register.html',
#            form_class=UserCreationForm,
#            success_url='/'
#    )),
#    url('^accounts/', include('django.contrib.auth.urls')),
]