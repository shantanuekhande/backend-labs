from django.db import models

# Create your models here.

class Course(models.Model):
    title  =models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)


    def __str__(self):
        return self.title
    
