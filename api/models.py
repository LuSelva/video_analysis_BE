from django.contrib.postgres.fields import ArrayField
from django.db import models


# REFERENCE LINK
# https://developerhowto.com/2018/12/10/using-database-models-in-python-and-django/

# QUERY
# https://docs.djangoproject.com/en/4.1/topics/db/sql/


class User(models.Model):
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    identifier = models.IntegerField(primary_key=True)
    email = models.CharField(max_length=62)
    password = models.CharField(max_length=50, default='0000000')
    admin = models.CharField(max_length=62, default='false')

    def __str__(self):
        return self.name


class Video(models.Model):
    name = models.CharField(max_length=50)
    identifier = models.IntegerField(primary_key=True)

    def __str__(self):
        return self.name


class Segment(models.Model):
    name = models.CharField(max_length=50)
    video_ref = models.ForeignKey(Video, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    type_val = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Analize(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)


class Evaluation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    segment_ref = models.ForeignKey(Segment, on_delete=models.CASCADE)
    type_val = models.CharField(max_length=50)
