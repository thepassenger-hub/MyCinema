from channels import Group
from channels.auth import channel_session_user, channel_session_user_from_http
from live_chat.signals import user_online, user_offline, mark_notifications_as_viewed
import json

# Notify to all users if their friends are online or offline.
# User is considered online if has an open session and is logged in.
# If he closes browser or logs out then he's considered offline.
@channel_session_user_from_http
def ws_connect(message):
    Group('users').add(message.reply_channel)
    if not message.user.is_anonymous: # User must be logged in
        user_online.send(sender=None, user=message.user) # Custom signal to change model field is_logged_in to True
        Group('users').send({
            'text': json.dumps({
                'username': message.user.username,
                'is_logged_in': message.user.profile.is_logged_in
            })
    })


@channel_session_user
def ws_disconnect(message):
    if not message.user.is_anonymous:
        user_offline.send(sender=None, user=message.user) # Custom signal to change model field is_logged_in to False
        Group('users').send({
            'text': json.dumps({
                'username': message.user.username,
                'is_logged_in': message.user.profile.is_logged_in
            })
    })
    Group('users').discard(message.reply_channel)

# Channel for live chat messages and notifications
@channel_session_user_from_http
def ws_chat_connect(message):
    message.reply_channel.send({"accept": True})
    if not message.user.is_anonymous:
        Group('%s' % message.user).add(message.reply_channel)

@channel_session_user
def ws_chat_message(message):
    if message.content['text'] == 'viewed' and not message.user.is_anonymous:
        mark_notifications_as_viewed.send(sender=None, user=message.user)

@channel_session_user
def ws_chat_disconnect(message):
    Group('%s' % message.user).discard(message.reply_channel)