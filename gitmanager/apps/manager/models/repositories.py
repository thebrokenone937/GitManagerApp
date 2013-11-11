from django.contrib.auth.models import User
from django.db import models


class Repositories(models.Model):
    name = models.CharField(max_length=100)
    user_id = models.ForeignKey(User,)
    git_url = models.CharField(max_length=255)
    repo_url = models.CharField(max_length=255)
    created = models.DateTimeField()
    is_del = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        app_label = 'manager'
        
        
class RepositoryUsers(models.Model):
    user_id = models.ForeignKey(User,)
    repository_id = models.ForeignKey(Repositories,)
    
    class Meta:
        app_label = 'manager'       
