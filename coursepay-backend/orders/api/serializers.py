from rest_framework import serializers


class CreateOrderSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    user_email = serializers.EmailField()
    
