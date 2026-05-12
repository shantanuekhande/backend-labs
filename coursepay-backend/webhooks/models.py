from django.db import models


class WebhookEvent(models.Model):

    event_id = models.CharField(
        max_length=255,
        unique=True
    )

    event_type = models.CharField(
        max_length=255
    )

    payload = models.JSONField()

    processed = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    processed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):

        return self.event_id