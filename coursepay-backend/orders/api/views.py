from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from orders.api.serializers import (
    CreateOrderSerializer
)

from payments.services.payment_service import (
    PaymentService
)


class CreateOrderAPIView(APIView):

    def post(self, request):

        serializer = CreateOrderSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        data = PaymentService.create_order(
            course_id=serializer.validated_data[
                "course_id"
            ],
            user_email=serializer.validated_data[
                "user_email"
            ]
        )

        return Response(
            data,
            status=status.HTTP_201_CREATED
        )