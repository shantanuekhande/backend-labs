from django.urls import path

from payments.api.views import (
    VerifyPaymentAPIView
)

urlpatterns = [
    path(
        "verify/",
        VerifyPaymentAPIView.as_view()

    )
]