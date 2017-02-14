from django.db.models import Q
from movie_app.models import Friendship


def get_friendship(user, friend):
    friendship = Friendship.objects.filter(Q(creator=user) & Q(friend=friend))
    if friendship:
        return friendship[0]
    else:
        return Friendship.objects.filter(Q(creator=friend) & Q(friend=user))[0]
