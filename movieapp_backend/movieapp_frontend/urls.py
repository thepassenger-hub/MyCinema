from django.conf.urls import url
from movieapp_frontend import views
urlpatterns = [
    url(r'^$', views.home_page, name='home_page'),
    url(r'^login/?$', views.login_page, name='login'),
    url(r'^logout/?$', views.logout_page, name='logout'),
    url(r'^signup/?$', views.signup, name='signup'),
]