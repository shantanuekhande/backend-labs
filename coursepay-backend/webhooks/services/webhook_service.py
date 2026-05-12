import json

from django.utils import timezone
from django.db import transaction
from django.conf import settings

from webhooks.models import (
    WebhookEvent
)

from payments.models import (
    Payment,
    PaymentStatus
)

from orders.models import (
    OrderStatus
)

from payments.services.razorpay_service import (
    RazorpayClient
)


class WebhookService:

    @staticmethod
    @transaction.atomic
    def process_razorpay_webhook(
        *,
        request_body,
        razorpay_signature
    ):

        client = RazorpayClient.get_client()

        # verify webhook signature
        client.utility.verify_webhook_signature(
            request_body,
            razorpay_signature,
            settings.RAZORPAY_WEBHOOK_SECRET
        )

        payload = json.loads(
            request_body
        )

        event_id = payload["payload"][
            "payment"
        ]["entity"]["id"]

        event_type = payload["event"]

        # idempotency
        webhook_event, created = (
            WebhookEvent.objects.get_or_create(
                event_id=event_id,

                defaults={
                    "event_type": event_type,
                    "payload": payload
                }
            )
        )

        if not created:
            return

        # handle payment captured
        if event_type == "payment.captured":

            razorpay_order_id = payload[
                "payload"
            ]["payment"]["entity"][
                "order_id"
            ]

            payment = (
                Payment.objects
                .select_for_update()
                .get(
                    razorpay_order_id=
                    razorpay_order_id
                )
            )

            if (
                payment.status
                != PaymentStatus.SUCCESS
            ):

                payment.status = (
                    PaymentStatus.SUCCESS
                )

                payment.razorpay_payment_id = (
                    event_id
                )

                payment.save()

                order = payment.order

                order.status = (
                    OrderStatus.COMPLETED
                )

                order.save()

        webhook_event.processed = True

        webhook_event.processed_at = (
            timezone.now()
        )

        webhook_event.save()