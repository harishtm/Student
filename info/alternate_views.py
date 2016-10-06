from django.contrib.auth.models import User
from django.http import Http404
from info.serializers import *
from info.models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics as g


class StudentList(g.ListAPIView):
    """
        Alternate for Student List 
        for many=True(avoiding)
    """

    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    paginate_by = 1

#    def get(self, request, format=None):
#        student_list = Student.objects.all()
#        serializer = StudentListSerializers(student_list)
#        return Response(serializer.data)


class AddStudent(g.CreateAPIView):
    """
        Similar to class based views (CreateView) CreateAPIView does same
        form_class is equal to serializer_class or even override post method
    """

    serializer_class = StudentListSerializers

    """
    def post(self, request, format=None):
        serializer = StudentSerializer(data=request.DATA)
        if serializer.is_valid():
            serializer.save()
            #return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({'status':True})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    """



    def get(self, request, format=None):
        student_list = Student.objects.all()
        serializer = StudentListSerializers(student_list)
        return Response(serializer.data)

