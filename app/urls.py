from django.conf.urls import url

from . import views

app_name = 'app'

urlpatterns = [

    url(r'^$', views.MainView.as_view(), name='main'),
]