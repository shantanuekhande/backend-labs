from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import razorpay

from webhooks.services.webhook_service import (
    WebhookService
)

class RazorpayWebhookAPIView(
    APIView
):

    authentication_classes = []

    permission_classes = []

    def post(self, request):

        print('WEBHOOK RECEIVED')
        print(request.body)
        signature = request.headers.get(
            "X-Razorpay-Signature"
        )
        print('SIGNATURE', signature)
        print('HEADERS', request.headers)

        try:
            WebhookService.process_razorpay_webhook(
                request_body=request.body.decode('utf-8'),
                razorpay_signature=signature
            )
        except razorpay.errors.SignatureVerificationError:
            return Response(
                {"error": "Invalid signature"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "message": "Webhook received"
            },
            status=status.HTTP_200_OK
        )