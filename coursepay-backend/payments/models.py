from django.db import models


class PaymentStatus(models.TextChoices):
    INITIATED = "INITIATED"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class Payment(models.Model):

    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE
    )

    razorpay_order_id = models.CharField(
        max_length=255,
        unique=True
    )

    razorpay_payment_id = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=50,
        choices=PaymentStatus.choices,
        default=PaymentStatus.INITIATED
    )

    created_at = models.DateTimeField(auto_now_add=True)