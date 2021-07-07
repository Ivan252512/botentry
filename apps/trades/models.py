from django.db import models

# Create your models here.


class Individual(models.Model):
    length = models.IntegerField()
    encoded_variables_quantity = models.IntegerField()
    mutation_intensity = models.IntegerField()
    dna = models.TextField()
    score = models.FloatField()
    min_value = models.IntegerField()
    max_value = models.IntegerField()
    pair = models.TextField()
    temp = models.TextField()
    created_date = models.DateTimeField(auto_now=True, auto_now_add=False)
    percent = models.FloatField()
    percent_divisor_increment = models.FloatField()

class Trade(models.Model):
    pair = models.TextField()
    operation = models.TextField()
    money = models.FloatField()
    price = models.FloatField()
    quantity = models.FloatField()   
    error = models.TextField(blank=True, null=True)
    traceback = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now=True, auto_now_add=False)