from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save
from movie_app.models import ChatMessage
from django.dispatch import receiver, Signal
from channels import Group
import json

@receiver(post_save, sender=ChatMessage)
def new_chat_message_callback(sender, instance, **kwargs):
    Group("%s" % instance.receiver.username).send({
        "text": json.dumps({
            "id": instance.id,
            "message": instance.message,
            "creator": instance.creator.username,
            "receiver": instance.receiver.username
        })
    })
    Group("%s" % instance.creator.username).send({
        "text": json.dumps({
            "id": instance.id,
            "message": instance.message,
            "creator": instance.creator.username,
            "receiver": instance.receiver.username
        })
    })

def set_user_online(sender, user, **kwargs):
    user.profile.is_logged_in = True
    user.profile.save()


def set_user_offline(sender, user, **kwargs):
    user.profile.is_logged_in = False
    user.profile.save()

user_online = Signal()
user_offline = Signal()

@receiver(user_online)
def user_online_callback(sender, user, **kwargs):
    set_user_online(sender, user, **kwargs)

@receiver(user_offline)
def user_offline_callback(sender, user, **kwargs):
    set_user_offline(sender, user, **kwargs)

@receiver(user_logged_in)
def user_logged_in_callback(sender, user, **kwargs):
    set_user_online(sender, user, **kwargs)

@receiver(user_logged_out)
def user_logged_out_callback(sender, user, **kwargs):
    set_user_offline(sender, user, **kwargs)



