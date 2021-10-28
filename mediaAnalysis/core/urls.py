from django.urls import path

from . import views


app_name = 'core'
urlpatterns = [
    path('', views.query, name='query'),
    path('query', views.query, name='query'),
]
