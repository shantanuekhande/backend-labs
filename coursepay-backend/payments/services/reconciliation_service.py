from django.utils import timezone
from django.db import transaction
from datetime import timedelta

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


class ReconciliationService:

    @staticmethod
    def reconcile_pending_payments():

        # find stale payments
        stale_time = (
            timezone.now()
            - timedelta(minutes=1)
        )

        pending_payments = (
            Payment.objects.filter(
                status=PaymentStatus.INITIATED,
                created_at__lte=stale_time
            )
        )

        print(
            f"Found {pending_payments.count()} stale payments"
        )

        client = RazorpayClient.get_client()

        for payment in pending_payments:

            try:

                # fetch latest order state
                # from Razorpay
                razorpay_order = (
                    client.order.fetch(
                        payment.razorpay_order_id
                    )
                )

                order_status = (
                    razorpay_order.get("status")
                )

                print(
                    f"Checking order:"
                    f" {payment.razorpay_order_id}"
                )

                print(
                    f"Gateway status:"
                    f" {order_status}"
                )

                # ---------------------------------
                # CASE 1 -> PAYMENT SUCCESS
                # ---------------------------------

                if order_status == "paid":

                    with transaction.atomic():

                        locked_payment = (
                            Payment.objects
                            .select_for_update()
                            .get(id=payment.id)
                        )

                        # idempotency protection
                        if (
                            locked_payment.status
                            == PaymentStatus.SUCCESS
                        ):
                            continue

                        locked_payment.status = (
                            PaymentStatus.SUCCESS
                        )

                        locked_payment.save()

                        order = locked_payment.order

                        order.status = (
                            OrderStatus.COMPLETED
                        )

                        order.save()

                        print(
                            "Payment reconciled successfully"
                        )

                # ---------------------------------
                # CASE 2 -> PAYMENT ABANDONED
                # ---------------------------------

                elif order_status == "created":

                    with transaction.atomic():

                        locked_payment = (
                            Payment.objects
                            .select_for_update()
                            .get(id=payment.id)
                        )

                        # already processed
                        if (
                            locked_payment.status
                            != PaymentStatus.INITIATED
                        ):
                            continue

                        locked_payment.status = (
                            PaymentStatus.FAILED
                        )

                        locked_payment.save()

                        order = locked_payment.order

                        order.status = (
                            OrderStatus.CANCELLED
                        )

                        order.save()

                        print(
                            "Expired stale payment"
                        )

                # ---------------------------------
                # CASE 3 -> UNKNOWN STATE
                # ---------------------------------

                else:

                    print(
                        f"Unhandled gateway status:"
                        f" {order_status}"
                    )

            except Exception as e:

                print(
                    f"Reconciliation failed:"
                    f" {str(e)}"
                )