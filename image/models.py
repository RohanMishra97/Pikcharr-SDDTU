from __future__ import unicode_literals
from django.contrib.auth.models import Permission, User
from django.db import models

# Create your models here.
class Album(models.Model):
	user = models.ForeignKey(User, default=1)
	album_title = models.CharField(max_length=500)
	album_cover = models.FileField()
	is_favorite = models.BooleanField(default=False)


class Pic(models.Model):
	album = models.ForeignKey(Album,on_delete=models.CASCADE)
	pic_title = models.CharField(max_length=100)
	pic_caption = models.CharField(max_length=1000)
	pic_file=models.FileField()
	is_favorite=models.BooleanField(default=False)
