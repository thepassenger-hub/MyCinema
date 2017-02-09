from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.


class MoviePost(models.Model):
    post_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    image_url = models.CharField(max_length=255, blank=True, null=True)
    rating = models.IntegerField()
    user = models.ForeignKey(User, related_name='posts')
    send_to = models.ManyToManyField(User, related_name='received_posts')
    content = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = 'movie_post'

class Friendship(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)
    creator = models.ForeignKey(User, related_name="friendship_creator_set")
    friend = models.ForeignKey(User, related_name="friend_set")

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, blank=True, null=True)
    avatar = models.ImageField(default="avatar.svg")
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

class FriendshipRequest(models.Model):
    from_user = models.ForeignKey(User, related_name="friendship_requests_sent")
    to_user = models.ForeignKey(User, related_name="friendship_requests_received")
    created = models.DateTimeField(auto_now_add=True)
    rejected = models.DateTimeField(blank=True, null=True)
    viewed = models.DateTimeField(blank=True, null=True)

    def accept(self):
        f = Friendship()
        f.creator = self.from_user
        f.friend = self.to_user
        f.save()

        self.delete()

        FriendshipRequest.objects.filter(
            from_user=self.to_user,
            to_user=self.from_user
        ).delete()

        return True

    def reject(self):
        """ reject this friendship request """
        self.rejected = timezone.now()
        self.save()

    def cancel(self):
        """ cancel this friendship request """
        self.delete()
        return True

    def mark_viewed(self):
        self.viewed = timezone.now()
        self.save()
        return True


