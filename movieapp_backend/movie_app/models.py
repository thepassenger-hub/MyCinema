from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class MoviePost(models.Model):
    post_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    image_url = models.CharField(max_length=255, blank=True)
    rating = models.IntegerField()
    user = models.ForeignKey(User, related_name='posts')
    send_to = models.ManyToManyField(User, related_name='received_posts')
    content = models.TextField(blank=True)

    class Meta:
        db_table = 'movie_post'

class Friendship(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)
    creator = models.ForeignKey(User, related_name="friendship_creator_set")
    friend = models.ForeignKey(User, related_name="friend_set")

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, blank=True)
    avatar = models.ImageField(upload_to='avatar_images/', blank=True)
    def get_friends(self):
        user = self.user
        friendships = Friendship.objects.filter(models.Q(creator=user)|models.Q(friend=user))
        friends = []
        for x in friendships:
            if x.creator == user:
                friends.append(x.friend)
            else:
                friends.append(x.creator)
        return friends




