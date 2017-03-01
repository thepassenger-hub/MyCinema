from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save
from movie_app.models import ChatMessage
from django.dispatch import receiver
from channels import Group
import json

# @receiver(post_save, sender=ChatMessage)
# def new_chat_message_callback(sender, instance, **kwargs):
#     Group("chat").send({
#         "text": json.dumps({
#             "id": instance.id,
#             "message": instance.message,
#             "creator": instance.creator,
#             "receiver": instance.receiver
#         })
#     })


@receiver(user_logged_in)
def user_logged_in_callback(sender, user, **kwargs):
    user.profile.is_logged_in = True
    user.profile.save()

@receiver(user_logged_out)
def user_logged_out_callback(sender, user, **kwargs):
    user.profile.is_logged_in = False
    user.profile.save()


