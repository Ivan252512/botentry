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
    pair = models.CharField(max_length=10)
    temp = models.CharField(max_length=5)
    created_date = models.DateTimeField(auto_now=True, auto_now_add=False)
