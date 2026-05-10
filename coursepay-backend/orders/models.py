from django.db import models

# Create your models here.
class OrderStatus(models.TextChoices):
    CREATED = 'CREATED'
    PAYMENT_PENDING = 'PAYMENT_PENDING' 
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'

class Order(models.Model):
    user_email = models.EmailField()
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.CREATED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)