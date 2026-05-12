from django.urls import path

from orders.api.views import (
    CreateOrderAPIView
)

urlpatterns = [
    path(
        "create/",
        CreateOrderAPIView.as_view()
    )
]