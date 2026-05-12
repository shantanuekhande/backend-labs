import razorpay
from django.conf import settings



class RazorpayClient:
    @staticmethod
    def get_client():
        client = razorpay.Client(
            auth=(settings.REZORPAY_KEY_ID, settings.REZORPAY_KEY_SECRET)
        )   
        return client
    
