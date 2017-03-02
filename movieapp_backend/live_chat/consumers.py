from channels import Group
from channels.auth import channel_session_user, channel_session_user_from_http
from live_chat.signals import user_online, user_offline
import json

# @channel_session_user_from_http
# def ws_chat(message):
#     Group('chat').send({
#             'text': json.dumps({
#                 'username': message.user.username,
#                 'is_logged_in':message.user.profile.is_logged_in
#             })
#         })

@channel_session_user_from_http
def ws_connect(message):
    Group('users').add(message.reply_channel)
    if not message.user.is_anonymous:
        user_online.send(sender=None, user=message.user)
        Group('users').send({
            'text': json.dumps({
                'username': message.user.username,
                'is_logged_in': message.user.profile.is_logged_in
            })
    })


@channel_session_user
def ws_disconnect(message):
    if not message.user.is_anonymous:
        user_offline.send(sender=None, user=message.user)
        Group('users').send({
            'text': json.dumps({
                'username': message.user.username,
                'is_logged_in': message.user.profile.is_logged_in
            })
    })
    Group('users').discard(message.reply_channel)

@channel_session_user_from_http
def ws_chat_connect(message):
    message.reply_channel.send({"accept": True})
    if not message.user.is_anonymous:
        Group('%s' % message.user).add(message.reply_channel)
    # Group('chat').send({
    #     'text': json.dumps({
    #         'username': message.user.username,
    #         'is_logged_in': message.user.profile.is_logged_in
    #     })
    # })

@channel_session_user
def ws_chat_disconnect(message):
    # Group('chat').send({
    #     'text': json.dumps({
    #         'username': message.user.username,
    #         'is_logged_in': message.user.profile.is_logged_in
    #     })
    # })
    Group('%s' % message.user).discard(message.reply_channel)