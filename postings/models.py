from django.db import models

class Posting(models.Model):
    housing_type = models.ForeignKey('HousingType', on_delete=models.CASCADE)
    item_color   = models.ForeignKey('Color', on_delete=models.CASCADE,related_name='posting_item_color')
    size         = models.ForeignKey('Size', on_delete=models.CASCADE)
    style        = models.ForeignKey('Style', on_delete=models.CASCADE)
    user         = models.ForeignKey('users.User', on_delete=models.CASCADE,related_name='posting') 
    back_color   = models.ForeignKey('Color', on_delete=models.CASCADE,related_name='posting_back_color')
    like         = models.ManyToManyField('users.User', through='Like',related_name='posting_like')
    image        = models.CharField(max_length=200)
    text         = models.TextField()
    create_at    = models.DateTimeField(auto_now_add=True)
    update_at    = models.DateTimeField()
    view         = models.IntegerField(default=0)
   
    class Meta:
        db_table = 'postings'
        
class Like(models.Model):
    user    =  models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='like' )
    posting =  models.ForeignKey(Posting, on_delete=models.CASCADE, related_name='like_posting') 
    
    class Meta:
        db_table = 'likes'
        
class HousingType(models.Model):
    type =  models.CharField(max_length=45)
    
    class Meta:
        db_table = 'housing_types'

class Color(models.Model):
    type =  models.CharField(max_length=45)
    
    class Meta:
        db_table = 'colors'
      
class Size(models.Model):
    type =  models.CharField(max_length=45)
    
    class Meta:
        db_table = 'sizes'

class Style(models.Model):
    type =  models.CharField(max_length=45)
    
    class Meta:
        db_table = 'styles'   