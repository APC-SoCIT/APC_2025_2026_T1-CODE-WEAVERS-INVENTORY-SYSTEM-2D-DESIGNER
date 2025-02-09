from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    address = models.TextField()

    def __str__(self):
        return self.user.username

class PreOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    design = models.ImageField(upload_to='designs/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PreOrder by {self.user.username} on {self.created_at}"
