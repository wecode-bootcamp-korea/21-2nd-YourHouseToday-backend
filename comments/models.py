from django.db import models

class Comment(models.Model):
    posting   = models.ForeignKey('postings.Posting', on_delete=models.CASCADE)
    user      = models.ForeignKey('users.User', on_delete=models.CASCADE)
    comment   = models.ForeignKey('self', on_delete=models.CASCADE, null=True,related_name='re_comment')
    text      = models.CharField(max_length=100)
    create_at = models.DateTimeField(auto_now_add=True) 
    update_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'comments'