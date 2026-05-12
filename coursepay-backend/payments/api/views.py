from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from payments.api.serializers import (
    VerifyPaymentSerializer
)

from payments.services.payment_service import (
    PaymentService
)


class VerifyPaymentAPIView(APIView):

    def post(self, request):

        serializer = VerifyPaymentSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        PaymentService.verify_payment(
            razorpay_order_id=serializer.validated_data[
                "razorpay_order_id"
            ],

            razorpay_payment_id=serializer.validated_data[
                "razorpay_payment_id"
            ],

            razorpay_signature=serializer.validated_data[
                "razorpay_signature"
            ]
        )

        return Response(
            {
                "message": "Payment verified"
            },
            status=status.HTTP_200_OK
        )