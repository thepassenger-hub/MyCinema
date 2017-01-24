from django.db import models

from django.contrib.auth.models import User
# Create your models here.
class MoviePost(models.Model):
    post_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    image_url = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()

    class Meta:
        db_table = 'movie_post'



