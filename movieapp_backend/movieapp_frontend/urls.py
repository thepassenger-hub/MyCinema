from django.conf.urls import url
from movieapp_frontend import views
urlpatterns = [
    url(r'^$', views.home_page, name='home_page'),
    url(r'^login/?$', views.login_page, name='login'),
    url(r'^logout/?$', views.logout_page, name='logout'),
    url(r'^signup/?$', views.signup, name='signup'),
    url(r'^newpost/?$', views.new_post_page, name='new_post'),
    url(r'^settings/?$', views.settings_page, name='settings'),
    url(r'^settings/change_name/?$', views.change_name, name='change_name'),
    url(r'^settings/change_password/$', views.change_password, name='change_password'),
    url(r'^settings/change_avatar/$', views.change_avatar, name='change_avatar'),
    url(r'^settings/delete_account/$', views.delete_account, name='delete_account'),
    url(r'^profile/(?P<user_id>\w+)/$', views.profile_page, name='profile_page'),
    url(r'^search_friends/$', views.search_friends_page, name='search_friends_page'),
    url(r'^friend/add/(?P<friend_user_id>\w+)/$', views.add_friend, name='add_friend'),
    url(r'^friend/accept/(?P<friend_request_id>\d+)/$', views.accept_friendship, name='friendship_accept'),
    url(r'^friend/reject/(?P<friend_request_id>\d+)/$', views.reject_friendship, name='friendship_reject'),
    url(r'^friend/delete/(?P<friend_user_id>\w+)/$', views.delete_friend, name='delete_friend'),
    url(r'^chat/(?P<friend_user_id>\w+)/$', views.chat, name='chat'),
    url(r'^notifications/$', views.notifications, name='notifications'),
]