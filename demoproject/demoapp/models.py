from django.db import models

# Create your models here.
from django.db import models

class VideoCaptured(models.Model):
   uuid=models.CharField(max_length = 100)
   image = models.ImageField(upload_to ='user_uploads',null=True)
   status=models.CharField(max_length = 50,blank=True)
   name = models.CharField(max_length = 150,blank=True)
   occupation=models.CharField(max_length = 15,blank=True,)
   created_at = models.CharField(max_length = 50)
   updated_at = models.CharField(max_length = 50)

   class Meta:
      db_table = "VideoCaptured"


class EventVideos(models.Model):
   evntname = models.CharField(max_length = 150,blank=True)
   path=models.CharField(max_length = 550,blank=True,)
   created_at = models.CharField(max_length = 50)
   updated_at = models.CharField(max_length = 50)
   class Meta:
      db_table = "EventVideos"

class Addcamera(models.Model):
   camname = models.CharField(max_length = 150,blank=True)
   camip=models.CharField(max_length = 550,blank=True,)
   purpose=models.CharField(max_length = 550,blank=True,)
   height=models.IntegerField(max_length = 550,blank=True,)
   width=models.IntegerField(max_length = 550,blank=True,)
   created_at = models.CharField(max_length = 50)
   updated_at = models.CharField(max_length = 50)
   class Meta:
      db_table = "Addcamera"
