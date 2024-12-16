from django.db import models
from django.utils.timezone import now

class TimestampModel(models.Model):
    created_at = models.DateTimeField(default=now)  
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        self.updated_at = now()
        super().save(*args, **kwargs)
        
    class Meta:
        abstract = True
        
        
class UserModel(models.Model):
    created_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="%(class)s_created_by")
    updated_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="%(class)s_updated_by")
    
    class Meta:
        abstract = True
    

class TimestampUserModel(TimestampModel, UserModel): 
        
    class Meta:
        abstract = True
        
    
