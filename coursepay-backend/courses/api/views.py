from rest_framework.views import APIView
from rest_framework.response import Response

from courses.models import Course
from courses.api.serializers import CourseSerializer


class CourseListAPIView(APIView):

    def get(self, request):

        courses = Course.objects.filter(
            is_active=True
        )

        serializer = CourseSerializer(
            courses,
            many=True
        )

        return Response(serializer.data)