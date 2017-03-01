from channels import Group
from channels.auth import channel_session_user, channel_session_user_from_http

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
    Group('users').send({
        'text': json.dumps({
            'username': message.user.username,
            'is_logged_in': message.user.profile.is_logged_in
        })
    })


@channel_session_user
def ws_disconnect(message):
    Group('users').send({
        'text': json.dumps({
            'username': message.user.username,
            'is_logged_in': message.user.profile.is_logged_in
        })
    })
    Group('users').discard(message.reply_channel)

# @channel_session_user_from_http
# def ws_chat_connect(message):
#     Group('chat').add(message.reply_channel)
#     Group('chat').send({
#         'text': json.dumps({
#             'username': message.user.username,
#             'is_logged_in': message.user.profile.is_logged_in
#         })
#     })
#
# @channel_session_user
# def ws_chat_disconnect(message):
#     Group('chat').send({
#         'text': json.dumps({
#             'username': message.user.username,
#             'is_logged_in': message.user.profile.is_logged_in
#         })
#     })
#     Group('chat').discard(message.reply_channel)