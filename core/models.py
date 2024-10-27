from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


class CustomUserModel(AbstractUser):
    pass


class UrlModel(models.Model):

    STATUS = (
        ('inactive','INACTIVE'),
        ('active', 'ACTIVE')
    )

    session_key = models.CharField(max_length=50, null=True, blank=True)
    original_link = models.URLField()
    unique_code = models.CharField(max_length=10, default='')
    date_added = models.DateField(auto_now_add=True)
    clicks = models.IntegerField(default=0)
    status = models.CharField(max_length=10, default='active', choices=STATUS)
    user = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE,  null=True, blank=True) # link can be created with user

    def __init__(self, *args, **kwargs):
        super(UrlModel, self).__init__(*args, **kwargs)
        if not self.unique_code:
            self.unique_code = str(uuid.uuid4())[:8]

    @staticmethod
    def check_max_limit_for_anon_users(session_key):
        link_count = UrlModel.objects.filter(session_key=session_key).count()
        if link_count >= 5:
            return True
        
        return False 
    
    @staticmethod
    def get_remaining_limit(session_key):
        link_count = UrlModel.objects.filter(session_key=session_key).count()
        return 5 - link_count

    def __str__(self):
        return str(self.unique_code)
    
