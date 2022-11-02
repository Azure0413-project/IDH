from django.db import models

# Create your models here.
class Patient(models.Model):
    p_id = models.IntegerField()
    p_name = models.CharField(max_length=10)