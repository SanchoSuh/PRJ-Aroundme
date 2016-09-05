from django.db import models
from django.conf import settings

class Member(models.Model) :
    name = models.TextField(max_length=20)
    birthday = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

