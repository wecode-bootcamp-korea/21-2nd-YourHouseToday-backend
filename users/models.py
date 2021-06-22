from django.db import models

class User(models.Model):
    email         = models.CharField(max_length=50)
    nickname      = models.CharField(max_length=50)
    introduction  = models.CharField(max_length=40, null=True)
    profile_image = models.CharField(max_length=200, null=True)
    kakao_id      = models.CharField(max_length=20)
    is_delete     = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'users'