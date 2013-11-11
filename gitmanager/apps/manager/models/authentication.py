from django.contrib.auth.models import User
from django.db import models

class PasswordResetTokens(models.Model):
    token = models.TextField(max_length=255)
    user_id = models.ForeignKey(User,)
    
    def __unicode__(self):
        return self.token
    
    class Meta:
        app_label = 'manager'