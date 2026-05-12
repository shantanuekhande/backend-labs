from courses.models import Course
from orders.models import Order, OrderStatus
from payments.models import Payment

from payments.services.razorpay_service import (RazorpayClient)



from django.db import transaction

from payments.models import (
    Payment,
    PaymentStatus
)

from orders.models import (
    OrderStatus
)


class PaymentService:

    @staticmethod
    def create_order(
        *,
        course_id,
        user_email
    ):

        # fetch course
        course = Course.objects.get(
            id=course_id,
            is_active=True
        )

        # backend controls amount
        amount = course.price
        amount_in_paise = int(amount * 100)

        # create internal order
        order = Order.objects.create(
            user_email=user_email,
            course=course,
            amount=amount,
            status=OrderStatus.PAYMENT_PENDING
        )

        client = RazorpayClient.get_client()

        # create razorpay order
        razorpay_order = client.order.create({
            "amount": amount_in_paise,
            "currency": "INR",
            "receipt": f"order_{order.id}"
        })

        # create payment row
        payment = Payment.objects.create(
            order=order,
            razorpay_order_id=razorpay_order["id"]
        )

        return {
            "order_id": order.id,
            "amount": str(amount),
            "currency": "INR",
            "razorpay_order_id": razorpay_order["id"],
            "razorpay_key": client.auth[0],
        }
    

    @staticmethod
    @transaction.atomic
    def verify_payment(
        *,
        razorpay_order_id,
        razorpay_payment_id,
        razorpay_signature
    ):

        client = RazorpayClient.get_client()

        data = {
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature
        }

        # cryptographic verification
        client.utility.verify_payment_signature(
            data
        )

        payment = Payment.objects.select_for_update().get(
            razorpay_order_id=razorpay_order_id
        )

        # idempotency protection
        if payment.status == PaymentStatus.SUCCESS:
            return payment

        payment.razorpay_payment_id = (
            razorpay_payment_id
        )

        payment.status = PaymentStatus.SUCCESS

        payment.save()

        order = payment.order

        order.status = OrderStatus.COMPLETED

        order.save()

        return payment