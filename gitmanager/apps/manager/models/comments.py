from django.contrib.auth.models import User
from django.db import models

class Comments(models.Model):
    comment = models.TextField()
    user_id = models.ForeignKey(User,)
    commit_hash = models.CharField(db_index=True, max_length=60)
    created = models.DateTimeField()
    is_del = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.comment
    
    class Meta:
        app_label = 'manager'