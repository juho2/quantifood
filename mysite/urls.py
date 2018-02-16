"""mysite URL Configuration

The `urlpatterns` list routes URLs to views.
"""
from django.conf.urls import include, url
from django.contrib import admin

from . import views
#from recommender import views as rec_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.index, name='index'),
#    url(r'^login/', views.login, name='login'),
#    url(r'^register/', rec_views.register, name='register'),
    url(r'^recommender/', include('recommender.urls')),
]
