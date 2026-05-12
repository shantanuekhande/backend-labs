from django.urls import path

from webhooks.api.views import (
    RazorpayWebhookAPIView
)

urlpatterns = [
    path(
        "razorpay/",
        RazorpayWebhookAPIView.as_view()
    )
]