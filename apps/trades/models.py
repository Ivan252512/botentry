from django.db import models

# Create your models here.

class USDTPair(models.Model):
    symbol = models.CharField(max_length=10)
    
    